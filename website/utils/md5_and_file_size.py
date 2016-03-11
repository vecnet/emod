import hashlib

DOWNLOAD_CHUNK_SIZE = 10240


def get_md5_and_file_size(data_source, supposed_file_size=None, callback_function=None, *args):
        bytes_processed = 0
        md5 = hashlib.md5()

        if supposed_file_size is None:
            percent_processed = -1

            if callback_function:
                callback_function(percent_processed, *args)

        while True:
            data = data_source.read(DOWNLOAD_CHUNK_SIZE)

            # There was no more data to read
            if not data:
                break

            bytes_processed += len(data)

            if supposed_file_size:
                percent_processed = float(bytes_processed / supposed_file_size * 100)

                if percent_processed > 10:
                    if callback_function:
                        callback_function(percent_processed, *args)

            md5.update(data)

        if callback_function:
            callback_function(100.0, *args)

        return md5.hexdigest(), bytes_processed