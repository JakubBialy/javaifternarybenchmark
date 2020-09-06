import io
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def read_text_file(filepath):
    with open(filepath, 'r') as file:
        return file.read()


def get_line_starting_with(txt, starts_with):
    first_index = txt.find(starts_with)
    last_index = txt.find('\n', first_index)

    return txt[first_index: last_index]


def detect_decimal_separator(txt):
    for line in txt.split('\n')[1:]:
        if ',' in line:
            return ','
        elif '.' in line:
            return '.'

    raise Exception("Sorry, separator cannot be detected")


def read_measures(filepath, add_java_version):
    result = pd.DataFrame()

    for subdir, dirs, files in os.walk(filepath):
        for file in files:
            filepath = subdir + os.sep + file

            txt = read_text_file(filepath)

            data_string = io.StringIO("\n".join([line for line in txt.split('\n') if ';' in line]))

            df = pd.read_csv(data_string, sep=';', decimal=detect_decimal_separator(txt))

            if add_java_version:
                java_version = file.replace('benchmark_', '').replace('.scsv', '').replace('-', '')
                df['java_version'] = java_version

            df['memory'] = pd.to_numeric(get_line_starting_with(txt, '-Xmx').replace('-Xmx', ''))

            result = result.append(df)

    return result


def generate_heatmap(measures, first_dimen, second_dimen, vals_dimen, output_file):
    plt.clf()
    current_df = measures

    # Index = current_df[first_dimen].unique()
    unique_y_vals = list(current_df[first_dimen].unique())
    string_prefix = commonprefix(unique_y_vals)

    Index = list(map(lambda str: str.replace(string_prefix, ''), unique_y_vals))
    Cols = current_df[second_dimen].unique()
    df = pd.DataFrame(current_df[vals_dimen].values.reshape(len(Index), len(Cols)), index=Index, columns=Cols)

    sns.heatmap(df, annot=True, fmt='.3g')
    # .set_title('Throughput of summing array elements (size: ' + str(current_elements_size) + ')')
    # plt.show()
    # plt.xlabel("Memory [GB]")
    # plt.ylabel("Java version")
    plt.xlabel(first_dimen)
    plt.ylabel(second_dimen)
    plt.savefig(output_file, bbox_inches="tight", dpi=150)


def commonprefix(m):
    "Given a list of pathnames, returns the longest common leading component"
    if not m: return ''
    s1 = min(m)
    s2 = max(m)
    for i, c in enumerate(s1):
        if c != s2[i]:
            return s1[:i]
    return s1


if __name__ == '__main__':
    input_dir = sys.argv[1:][0]
    output_file = sys.argv[1:][1]

    add_java_version_as_dimension = sys.argv[1:][2].lower() == "true"
    heatmap = len(sys.argv[1:]) == 4
    second_dimension = sys.argv[1:][3]

    if add_java_version_as_dimension:
        measures = read_measures(input_dir, True).sort_values(by='java_version')
    else:
        measures = read_measures(input_dir, False)

    if heatmap:
        generate_heatmap(measures, second_dimension, 'java_version', 'Score', output_file)
    else:
        iterations_set = measures[second_dimension].unique()
        for current_iterations_param in iterations_set:
            fig = plt.figure()
            data_for_current_iterations_param = measures[measures[second_dimension] == current_iterations_param]

            test_names = np.unique(data_for_current_iterations_param['Benchmark'].to_numpy())

            # for test_name in test_names:
            for test_name in test_names[0:1]:
                data_subset = data_for_current_iterations_param[
                    data_for_current_iterations_param['Benchmark'] == test_name]
                # plt.errorbar(data_subset['java_version'], data_subset['Score'], data_subset['Score Error (99,9%)'],
                plt.errorbar(data_subset['java_version'], data_subset['Score'],
                             data_subset[[col for col in measures.columns if 'Score Error' in col][0]],
                             label=test_name, lw=0.5, capsize=5, capthick=0.5, marker='o', markersize=2)

            plt.title("Sum of {:d} elements".format(current_iterations_param))
            plt.xlabel("Java version")
            plt.ylabel("Throughput [ops/s]")
            plt.xticks(rotation='vertical')
            plt.savefig(output_file, bbox_inches="tight", dpi=150)

    # if 'Param: ELEMENTS' in measures:
    #     iterations_set = measures['Param: ELEMENTS'].unique()
    #     for current_iterations_param in iterations_set:
    #         fig = plt.figure()
    #         data_for_current_iterations_param = measures[measures['Param: ELEMENTS'] == current_iterations_param]
    #
    #         test_names = np.unique(data_for_current_iterations_param['Benchmark'].to_numpy())
    #
    #         # for test_name in test_names:
    #         for test_name in test_names[0:1]:
    #             data_subset = data_for_current_iterations_param[
    #                 data_for_current_iterations_param['Benchmark'] == test_name]
    #             # plt.errorbar(data_subset['java_version'], data_subset['Score'], data_subset['Score Error (99,9%)'],
    #             plt.errorbar(data_subset['java_version'], data_subset['Score'],
    #                          data_subset[[col for col in measures.columns if 'Score Error' in col][0]],
    #                          label=test_name, lw=0.5, capsize=5, capthick=0.5, marker='o', markersize=2)
    #
    #         plt.title("Sum of {:d} elements".format(current_iterations_param))
    #         plt.xlabel("Java version")
    #         plt.ylabel("Throughput [ops/s]")
    #
    #         plt.xticks(rotation='vertical')
    #         plt.savefig(output_file, bbox_inches="tight", dpi=150)
    # else:
    #     fig = plt.figure()
    #     data_for_current_iterations_param = measures
    #
    #     test_names = np.unique(data_for_current_iterations_param['Benchmark'].to_numpy())
    #
    #     # for test_name in test_names:
    #     for test_name in test_names[0:1]:
    #         data_subset = data_for_current_iterations_param[data_for_current_iterations_param['Benchmark'] == test_name]
    #         # plt.errorbar(data_subset['java_version'], data_subset['Score'], data_subset['Score Error (99,9%)'],
    #         plt.errorbar(data_subset['java_version'], data_subset['Score'],
    #                      data_subset[[col for col in measures.columns if 'Score Error' in col][0]],
    #                      label=test_name, lw=0.5, capsize=5, capthick=0.5, marker='o', markersize=2)
    #
    #     # plt.title("Sum of {:d} elements".format(current_iterations_param))
    #     plt.xlabel("Java version")
    #     plt.ylabel("Throughput [ops/s]")
    #
    #     plt.xticks(rotation='vertical')
    #     plt.savefig(output_file, bbox_inches="tight", dpi=150)
