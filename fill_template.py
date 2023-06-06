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
    if args.tex_out_dir is not None:
        os.system(f'cp {temp_dir}/checklist_{id}.tex {args.tex_out_dir}')


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

        # Some consideration for how to format things with respect to their use for later analysis. There are technically 4 possible responses to the non-text 
        # part of the checklist: Yes, No, N/A, Select. 

        # Emma, for the proposal to record the "Not Applicable" answers in the text box, how would we handle instances where the response is N/A and there 
        # is also a comment in the text box? I think we can prepend "Not Applicable" to the text, as that would look natural. But it would also be great 
        # if we use some kind of unique punctuation around the Not Applicable (e.g. "[] <Question>\nNot Applicable: <Some text from user comment>"), 
        # so researchers can consistently extract the label from the PDF data if necessary.

        # Select is also a tricky one, as it does really provide important information that the author didn't interact with the drop down menu 
        # at all rather than affirmatively selecting the "No" option. So my preference would be that we record when this happens in some way. 
        # Perhaps when a question is select, we could render this as "[] <Question>\nNo Response"

        na_store = False  # whether the previous non-text field was "N/A"; used to augment following text response.
        select_store = False  # whether the previous non-text field was "Select" (i.e. no response); used to augment following text response.
        for col in checklist_df.columns:

            is_text_col = col[-4:] == "text"
            
            if pd.isnull(row[col]):
                if is_text_col:
                    row[col] = "Left blank."
                else:
                    row[col] = "$\square$"
            if row[col] == 'Select':
                if is_text_col:
                    row[col] = "No response."
                else:
                    row[col] = "$\square$"
                    select_store = True
            if row[col] == "Not applicable":
                row[col] = "$\square$"
                na_store = True
            if row[col] == 'Yes':
                row[col] = "\yes"
            if row[col] == 'No':
                row[col] = "$\square$"
            
            if is_text_col and na_store:
                row[col] = "Not applicable. " + row[col]
                na_store = False
            if is_text_col and select_store:
                row[col] = "No response."
                select_store = False
            
            template = template.replace(f'{{{{{col}}}}}', str(row[col]))

        print(template)
        
        # check for missing responses
        missing_responses = re.findall(r'\{\{.*\}\}', template)
        if missing_responses:
            if args.remove_missing:
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
    parser.add_argument('--tex_out_dir', type=str)
    parser.add_argument('--remove_missing', action='store_true')
    args = parser.parse_args()
    main(args)