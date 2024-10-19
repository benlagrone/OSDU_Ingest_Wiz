# Steps and Scripts for Processing

1. **Setup Environment**
   - **Action**: Create a folder and download necessary files.
   - **Directory**: `data/pdf/`

2. **Obtain Token**
   - **Tool**: Postman
   - **Script**: `make-token.py`
   - **Action**: Run the script to generate `token.json`.

3. **Create Legal Tag**
   - **Script**: `legal-tag.py`
   - **Action**: Execute to create a legal tag.

4. **Create Index**
   - **Script**: `index_pdf.py`
   - **Action**: Run to create an index for the PDFs.

5. **Get Storage Instructions**
   - **Script**: `get-storage-instructions.py`
   - **Action**: Execute to retrieve storage instructions.

6. **Upload Files**
   - **Script**: `upload-file-signed-url.py`
   - **Action**: Use the script to upload files using signed URLs.

7. **Register Dataset**
   - **Script**: `register-datasets.py`
   - **Action**: Run to register the dataset.

8. **Delete Registries**
   - **Script**: `delete-registries.py`
   - **Action**: Execute to delete all registries.
