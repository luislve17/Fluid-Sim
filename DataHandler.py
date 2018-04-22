import numpy as np

class DataHandler:
    def load_data(self, data_path):
        file = open(data_path, 'r').read()
        all_data = file.split("\n=====\n")

        n_row, n_col, n_timestamps = all_data[0].split(" ")
        n_row, n_col, n_timestamps = int(n_row), int(n_col), int(n_timestamps)

        timestamps = []

        for t in range(1, n_timestamps):
            rows = all_data[t].split("\n")
            temp_matrix = [[i for i in r.split(" ")] for r in rows]

            for row in temp_matrix:
                del row[-1]

            timestamp_matrix = np.array(temp_matrix).astype(np.float)
            timestamps.append(timestamp_matrix)
        return (timestamps)

    def gen_example_data(self, data_name, n_row, n_col, num_timestamps):
        file = open(data_name, "w")

        file.write("{} {} {}\n".format(n_row, n_col, num_timestamps))
        file.write("=====\n")

        x = np.arange(0, 10, .1)

        for t in range(0, num_timestamps):
            for i in range(0, n_row):
                for j in range(0, n_col):
                    file.write("{} ".format(str(j*np.sin(t/50) + i**2/30)))
                file.write("\n")
            file.write("=====\n")
        file.close()
        print("Data de ejemplo generada")
