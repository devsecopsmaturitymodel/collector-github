import click
import yaml


class TeamsConfiguration:
    @classmethod
    def load(cls, config_file: click.File):
        try:
            return yaml.safe_load(config_file.read())
        except yaml.YAMLError as e:
            print("Error while parsing YAML file:")
            if hasattr(e, 'problem_mark'):
                if e.context is not None:
                    print(str(e.problem_mark) + '\n  ' +
                          str(e.problem) + ' ' + str(e.context) +
                          '\nPlease correct data and retry.')
                else:
                    print(str(e.problem_mark) + '\n  ' +
                          str(e.problem) + '\nPlease correct data and retry.')
            else:
                print("Something went wrong while parsing yaml file")
            return
