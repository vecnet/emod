$(document).ready(function()
{
    remove_spinner();
});

function add_spinner()
{
    $("#page-load-spinner").show();
    $("#page-content").css("display", "none");
}

function remove_spinner()
{
    $("#page-content").css("display", "");
    $("#page-load-spinner").hide();
}