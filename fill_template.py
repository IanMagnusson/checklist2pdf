import pandas as pd
import argparse
import re
import tempfile
import os

def compile_pdf(template, args, id):
    # copy other files in template directory to "temp"
    temp_dir = tempfile.mkdtemp()
    for file in os.listdir(os.path.dirname(args.template)):
        if file == os.path.basename(args.template):
            continue
        os.system(f'cp {os.path.dirname(args.template)}/{file} {temp_dir}')

    # write template to temp dir
    with open(f'{temp_dir}/checklist_{id}.tex', 'w') as f:
        f.write(template)

    # compile pdf
    os.system(f'cd {temp_dir}; whoami; pwd; ls -la;  pdflatex checklist_{id}.tex')

    # copy pdf to output directory
    os.system(f'cp {temp_dir}/checklist_{id}.pdf {args.pdf_out_dir}')

    # clean up
    os.system(f'rm -rf {temp_dir}')


def main(args):
    # read in checklist data
    checklist_df = pd.read_csv(args.checklist_data)

    # for each submission, fill in the template and make a pdf
    for i, row in checklist_df.iterrows():
        with open(args.template, 'r') as f:
            template = f.read()
        id = row['Submission ID']

        # fill each response
        for col in checklist_df.columns:
            if pd.isnull(row[col]):
                row[col] = 'Left Blank'
            if row[col] == 'Select':
                row[col] = 'Left Blank'
            if col == 'Submission ID':
                continue
            template = template.replace(f'{{{{{col}}}}}', str(row[col]))
        
        # check for missing responses
        missing_responses = re.findall(r'\{\{.*\}\}', template)
        if args.remove_missing and missing_responses:
            template = re.sub(r'\{\{.*\}\}', '', template)
        else:
            raise ValueError(f'Missing responses for {id}: {missing_responses}')

        # compile pdf
        compile_pdf(template, args, id)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--checklist_data', type=str)
    parser.add_argument('--template', type=str)
    parser.add_argument('--pdf_out_dir', type=str)
    parser.add_argument('--remove_missing', action='store_true')
    args = parser.parse_args()
    main(args)