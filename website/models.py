from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now

from jsonfield import JSONField
from vecnet.simulation import sim_model, sim_status
from website.utils.md5_and_file_size import get_md5_and_file_size


class RemoveDeletedManager(models.Manager):
    def get_queryset(self):
        # Not exactly sure why PyCharm code inspector does not like 'super' below
        # Code is based on https://docs.djangoproject.com/en/1.8/topics/db/managers/
        return super(RemoveDeletedManager, self).get_queryset().filter(deletion_timestamp__isnull=False).exclude(deletion_timestamp="")


class ModelVersion(models.Model):
    number = models.TextField(default=None)  # Using default=None to force an integrity issue if there is not a value provided

    class Meta:
        db_table = "model_version"
        verbose_name = "ModelVersion"
        verbose_name_plural = "ModelVersions"


class SimulationGroup(models.Model):
    """
    Represents a group of simulations submitted for execution at the same time.
    """
    submitted_by = models.ForeignKey(User)

    creation_timestamp = models.DateTimeField(auto_now_add=True)
    last_modified_timestamp = models.DateTimeField(auto_now=True)
    submission_timestamp = models.DateTimeField(null=True, blank=True)
    start_timestamp = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "%s" % self.id

    class Meta:
        db_table = "simulation_group"
        verbose_name = "SimulationGroup"
        verbose_name_plural = "SimulationGroup"


class Simulation(models.Model):
    """
    Represents a single execution of a simulation model.  Contains sufficient information about the particular
    simulation model that was run and the input data so that the output data can be reproduced.
    """
    group = models.ForeignKey(SimulationGroup, related_name="simulations")
    version = models.ForeignKey(ModelVersion)

    command_line_arguments = models.TextField(null=True, blank=True)
    status = models.ForeignKey()

    creation_timestamp = models.DateTimeField(auto_now_add=True)
    last_modified_timestamp = models.DateTimeField(auto_now=True)
    execution_start_timestamp = models.DateTimeField(null=True, blank=True)  # Collected on the cluster
    execution_end_timestamp = models.DateTimeField(null=True, blank=True)  # Collected on the cluster

    @property
    def execution_duration_as_timedelta(self):
        """
        Get the simulation's duration as a Python timedelta object.
        """
        if self.execution_start_timestamp is None or self.execution_end_timestamp is None:
            return None

        return self.execution_end_timestamp - self.execution_start_timestamp

    def copy(self, should_include_output=False):
        simulation_group = SimulationGroup(submitted_by=self.group.submitted_by)
        simulation_group.save()

        new_simulation = Simulation.objects.create(
            group=simulation_group,
            version=self.version,
            status=
        )

        # Add simulation input files to the new simulation
        for input_file in self.input_files.all():
            new_simulation.input_files.add(input_file)

        if should_include_output:
            # Add simulation output files to the new simulation
            for output_file in self.output_files.all():
                new_simulation.output_files.add(output_file.copy())

        return new_simulation

    def __str__(self):
        return "%s (v%s) - %s" % (self.id, self.version, self.status)

    class Meta:
        db_table = "simulation"
        verbose_name = "Simulation"
        verbose_name_plural = "Simulations"


class SimulationFile(models.Model):
    """
    Base class for a simulation's data file (input files and output files).
    """
    name = models.TextField(default=None)  # Using default=None to force an integrity issue if there is not a value provided
    file = models.FileField(default=None)  # Using default=None to force an integrity issue if there is not a value provided
    md5 = models.TextField(default=None)  # Using default=None to force an integrity issue if there is not a value provided
    size = models.BigIntegerField()

    def _get_size(self):
        return self.file.size

    def _update_md5_progress(self, ):
        print

    def get_contents(self):
        return self.file.read()

    def _set_contents(self, contents, is_binary=True):
        self.md5, self.size = get_md5_and_file_size(
            data_source=self.get_contents(), supposed_file_size=self.file.size,
            callback_function=self._update_md5_progress
        )

        self.save()

    def copy(self):
        if isinstance(self, SimulationInputFile):
            new_simulation_file = SimulationInputFile.objects.create_file(
                contents=self.get_contents(),
                name=self.name,
                metadata=self.metadata,
                created_by=self.created_by
            )
        elif isinstance(self, SimulationOutputFile):
            new_simulation_file = SimulationOutputFile.objects.create_file(
                contents=self.get_contents(),
                name=self.name,
                metadata=self.metadata,
            )
        else:
            raise Exception("SimulationFile is not of type SimulationInputFile nor SimulationOutputFile")

        return new_simulation_file

    def __str__(self):
        return "%s - %s" % (self.id, self.name)

    class Meta:
        abstract = True
        db_table = "simulation_file"
        verbose_name = "SimulationFile"
        verbose_name_plural = "SimulationFiles"


class SimulationFileModelManager(models.Manager):
    """
    Custom model manager for the data models representing simulation files.
    """

    def create_file(self, contents, **kwargs):
        sim_file = self.create(**kwargs)
        sim_file._set_contents(contents)
        return sim_file


class SimulationInputFile(SimulationFile):
    """
    An input file for a simulation.  An input file can be shared among multiple simulations.  An input file is
    immutable since it represents all or some of the data fed into a particular execution of the simulation model.  If
    it is altered, then it's no longer possible to reproduce the output from the simulation.

    An input file at this conceptual level is different than the concept at the user's perspective.  From her viewpoint,
    an input file is mutable.  For example, an OpenMalaria user can create a scenario file and then run a simulation
    with it.  After examining the simulation's output, she makes some changes in the scenario and re-runs it.  From her
    perspective, the two simulations were run with different versions of a single scenario file.  Those two versions
    of that scenario file would be represented by two instances of this class.  Their relationship as snapshots of the
    same scenario file would be stored in another data model.
    """
    simulations = models.ManyToManyField(Simulation,
                                         help_text='the simulations that used this file as input',
                                         related_name='input_files')
    created_by = models.ForeignKey(DimUser,
                                   help_text='who created the file')
    created_when = models.DateTimeField(help_text='when was the file created',
                                        auto_now_add=True)

    objects = SimulationFileModelManager()

    def set_contents(self, contents):
        simulations = self.simulations.all()

        if len(simulations) > 1:
            raise RuntimeError("File is shared by multiple simulations.")

        if len(simulations) == 0 or simulations[0].status == sim_status.READY_TO_RUN:
            self._set_contents(contents)
        else:
            raise RuntimeError("Simulation is not ready to run.")


class SimulationOutputFile(SimulationFile):
    """
    An output file produced by a simulation.
    """
    simulation = models.ForeignKey(Simulation,
                                   null=True,
                                   blank=True,
                                   help_text='the simulation that produced this file')

    objects = SimulationFileModelManager()


class Folder(models.Model):
    name = models.TextField()
    description = models.TextField(null=True, blank=True)

    parent_folder = models.ForeignKey("self", null=True, blank=True)
    owner = models.ForeignKey(User)

    is_public = models.BooleanField(default=False)
    sort_order = models.IntegerField()

    creation_timestamp = models.DateTimeField(auto_now_add=True)
    last_modified_timestamp = models.DateTimeField(auto_now=True)
    deletion_timestamp = models.DateTimeField(null=True, blank=True)

    all_objects = models.Manager()  # Default manager - will include deleted as well
    objects = RemoveDeletedManager()  # Override default manager to exclude deleted

    class NotEmpty(Exception):
        pass

    def delete_folder(self):
        if not self.is_empty:
            raise self.NotEmpty
        else:
            self.deletion_timestamp = now()
            self.save()

    @property
    def is_empty(self):
        subfolder_list = Folder.objects.filter(parent_folder=self.id)
        something_list = Something.objects.filter(folder=self.id)

        if subfolder_list.count() == 0 and something_list.count() == 0:
            return True
        else:
            return False

    class Meta:
        db_table = "folder"
        verbose_name = "Folder"
        verbose_name_plural = "Folders"


class Location(models.Model):
    name = models.TextField()
    description = models.TextField(null=True, blank=True)

    latitude = models.DecimalField(decimal_places=4, max_digits=7)
    longitude = models.DecimalField(decimal_places=4, max_digits=7)

    class Meta:
        db_table = "location"
        verbose_name = "Location"
        verbose_name_plural = "Locations"


class Baseline(models.Model):
    name = models.TextField()
    description = models.TextField(null=True, blank=True)

    simulation = models.ForeignKey(Simulation)
    location = models.ForeignKey(Location)

    creation_timestamp = models.DateTimeField(auto_now_add=True)
    last_modified_timestamp = models.DateTimeField(auto_now=True)
    deletion_timestamp = models.DateTimeField(null=True, blank=True)

    all_objects = models.Manager()  # Default manager - will include deleted as well
    objects = RemoveDeletedManager()  # Override default manager to exclude deleted

    @property
    def version(self):
        return self.simulation.version

    class Meta:
        db_table = "baseline"
        verbose_name = "Baseline"
        verbose_name_plural = "Baselines"