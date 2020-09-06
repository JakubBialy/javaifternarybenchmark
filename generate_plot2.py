import argparse
import io
import os
import re
from enum import Enum

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


class OutputMode(Enum):
    single_plot = 'single_plot'
    multi_plot = 'multi_plot'
    heatmap = 'heatmap'

    def __str__(self):
        return self.value


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def validate_dir_path(path):
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")


def validate_file_path(path):
    if os.path.isfile(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid file path")


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


def read_measures(filepath, filename_regex_filter, add_java_version):
    result = pd.DataFrame()

    for subdir, dirs, files in os.walk(filepath):
        for file in files:
            if not re.match(filename_regex_filter, file) is None:
                filepath = subdir + os.sep + file
                txt = read_text_file(filepath)
                data_string = io.StringIO("\n".join([line for line in txt.split('\n') if ';' in line]))
                df = pd.read_csv(data_string, sep=';', decimal=detect_decimal_separator(txt))
                # df = df[df[third_dimen].apply(lambda x: x > 0 or x <= 0)] # remove nans
                df = df[df[third_dimen].apply(lambda x: not pd.isnull(x))] # remove nans
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


def generate_single_plot():
    pass


def generate_multi_plot(measures, error_column_name, xlabel=None, ylabel=None):
    for current_second_dimen_value in measures[second_dimen].unique():
        data_filtered_by_second_dimen = measures[measures[second_dimen] == current_second_dimen_value]

        current_series = pd.DataFrame()
        for current_first_dimen_value in measures[first_dimen].unique():
            current_series = current_series.append(
                data_filtered_by_second_dimen[data_filtered_by_second_dimen[first_dimen] == current_first_dimen_value])

        if len(error_column_name) == 0:
            plt.errorbar(current_series[first_dimen],
                         current_series[third_dimen],
                         label=current_second_dimen_value,
                         lw=0.5, capsize=5, capthick=0.5, marker='o', markersize=2)
        else:
            plt.errorbar(current_series[first_dimen],
                         current_series[third_dimen],
                         current_series[[col for col in measures.columns if error_column_name in col][0]],
                         label=current_second_dimen_value,
                         lw=0.5, capsize=5, capthick=0.5, marker='o', markersize=2)

    if not xlabel is None:
        plt.xlabel(xlabel)
    else:
        plt.xlabel(first_dimen)

    if not ylabel is None:
        plt.ylabel(ylabel)
    else:
        plt.ylabel(third_dimen)

    plt.xticks(rotation='vertical')
    leg = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    plt.savefig(output_file, bbox_inches="tight", bbox_extra_artists=(leg,), dpi=150)


def parser_add_arguments():
    parser.add_argument("--extract-jdk-version", type=str2bool, nargs='?', const=True, default=False,
                        help="Extract jdk version.")
    parser.add_argument("--remove-first-dimen-common-prefixes", type=str2bool, nargs='?', const=True, default=False,
                        help="Extract jdk version.")
    parser.add_argument("--remove-second-dimen-common-prefixes", type=str2bool, nargs='?', const=True, default=False,
                        help="Extract jdk version.")
    parser.add_argument("--input-file-filter", type=str, nargs='?', const=True, default='.*\.(s){0,1}csv', required=False,
                        help="Extract jdk version.")
    parser.add_argument("--error-name", type=str, nargs='?', const=True, default='', help="Extract jdk version.")
    parser.add_argument('--input-dir', type=validate_dir_path, required=True)
    parser.add_argument('--output-file', type=str, required=True)
    parser.add_argument('--output-mode', type=OutputMode, choices=list(OutputMode), required=True)
    parser.add_argument('--first-dimen', type=str, required=True)
    parser.add_argument('--second-dimen', type=str, required=True)
    parser.add_argument('--third-dimen', type=str, required=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser_add_arguments()
    args = parser.parse_args()

    extract_jdk_version = args.extract_jdk_version
    input_dir = args.input_dir
    output_file = args.output_file
    first_dimen = args.first_dimen
    input_file_filter = args.input_file_filter
    second_dimen = args.second_dimen
    third_dimen = args.third_dimen
    output_mode = args.output_mode
    error_name = args.error_name
    remove_first_dimen_common_prefixes = args.remove_first_dimen_common_prefixes
    remove_second_dimen_common_prefixes = args.remove_second_dimen_common_prefixes

    if extract_jdk_version:
        measures = read_measures(input_dir, input_file_filter, True).sort_values(by='java_version')
    else:
        measures = read_measures(input_dir, input_file_filter, False)

    if remove_second_dimen_common_prefixes:
        common_prefix = commonprefix(list(measures[second_dimen]))
        measures[second_dimen] = measures[second_dimen].str.replace(common_prefix, '')

    if output_mode == OutputMode.heatmap:
        generate_heatmap(measures, second_dimen, 'java_version', 'Score', output_file)
    elif output_mode == OutputMode.single_plot:
        generate_single_plot()
    elif output_mode == OutputMode.multi_plot:
        generate_multi_plot(measures, error_name, ylabel="Throughput [ops/s]")

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
