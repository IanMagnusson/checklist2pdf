# checklist2pdf

## Setup
1) Install MacTeX:
- Visit the MacTeX website at http://www.tug.org/mactex/ and download the latest MacTeX distribution.
- Once downloaded, double-click on the .pkg file to start the installation. Follow the instructions to complete the installation.
2) Make python environment:
    ```
    pip install -r requirements.txt
    ```

## Usage
```
python fill_template.py --checklist_data path/to/csv/data --template templates/acl/acl_latex.tex --pdf_out_dir path/to/output
```

If your template has fields that do not have equivalent columns in your csv this will throw an error unless you use `--remove_missing` to remove these fields