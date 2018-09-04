"""Simple command parser for Blinky eyeblink detection application. Run Blinky in command line or in
the GUI"""
import sys
import argparse
import blinky_app
from pathlib import Path

input_file = None
parameters_file = None
output_file = None
cascade_file = Path('./haar_cascades/haarcascade_eye.xml')
gui = False

def run_parser():
    """Setup parser."""
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='define input file')
    parser.add_argument('-p', '--parameters', help='define parameters file')
    parser.add_argument('-o', '--output', help='define output csv-file')
    parser.add_argument('-c', '--cascade', help='define haar cascade file for detecting eye')
    parser.set_defaults(func=process_args)

    args = parser.parse_args()
    args.func(args)

def process_args(args):
    """Parse user inputs. Generates parameters and output file names if not given."""
    global input_file, parameters_file, output_file, cascade_file, gui
    if args.input:
        input_file = Path(args.input)
        if args.parameters:
            parameters_file = Path(args.parameters)
        else:
            parameters_file = input_file.with_suffix('.prm')

        if args.output:
            output_file = Path(args.output)
        else:
            output_file = input_file.with_suffix('.csv')

        if args.cascade:
            cascade_file = Path(args.cascade)

        if not input_file.exists():
            sys.exit("Video file not found!")

        if not cascade_file.exists():
            sys.exit("Haar Cascade file missing!")

        print("\nInput file '{}'".format(input_file))
        print("Parameters file '{}'".format(parameters_file))
        print("Output file '{}'".format(output_file))
        print("Cascade file '{}'".format(cascade_file))

    else:
        # Run GUI if no arguments given
        print("Running Blinky GUI")
        gui =  True


def main():
    run_parser()
    blinky_app.run(input_file, parameters_file, output_file, cascade_file, gui)


if __name__ == "__main__":
    main()
