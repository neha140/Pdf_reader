from PyPDF2 import PdfReader
from PIL import Image
import pytesseract
import re
import io
import streamlit as st
import pandas as pd


reader = PdfReader("sample.pdf")
number_of_pages = len(reader.pages)
textpage =[]
imagepage=[]
invoicepage =[]
text_imagepage =[]
count = 0


invoice_details={}
inv_title = ''
inv_no = ''
inv_date = ''
inv_name = ''
inv_address = ''
inv_amount = ''
inv_content = ''


st.title('File Uploader with PDF Handling')

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    
    
    if uploaded_file.type == "application/pdf":
        reader = PdfReader(uploaded_file)
        number_of_pages = len(reader.pages)
        file_name = uploaded_file.name
        st.title("PDF Reader")
        st.write("File name:", uploaded_file.name)
    #Extract data

        for num in range(number_of_pages):
            #textpage
            page = reader.pages[num] 

            text = page.extract_text()
            for char in text:
                if char.isalpha():
                    count +=1
            if count>0:
                textpage.append(num)
            text = ''
            count = 0


            #imagepage
            for image_file_object in page.images:
                image_data = image_file_object.data
                img = Image.open(io.BytesIO(image_data))
                text = pytesseract.image_to_string(img)
                # check if it's an invoice page
                invoice_no_match = re.search(r'Invoice:\s*(\S+)', text)
                invoice_no = invoice_no_match.group(1) if invoice_no_match else None
                if invoice_no!= None:
                    invoicepage.append(num)
                    inv_no = invoice_no
                
                    address_block_match = re.search(r'^([^\n]+?)\s+\d{1,5}\s+', text)
                    invoice_date_match = re.search(r'Invoice Date:\s*([\d.]+)', text)
                    name_match = re.search(r'Billto: =\s*([A-Za-z]+ [A-Za-z]+)', text)
                    address_match = re.search(r'Billto: =\s*[\w\s]+\n([\s\S]+?)(?=\n[A-Za-z ]+:|\n(?:Description|Subtotal|Total|Amount Paid)|$)', text)
                    total_amount_match = re.search(r'Price Amount:\s*([\d.]+)', text)
                    description_match = re.search(r'Description\s+Quantity\s+Unit\n\n(Consultation \d+ each)', text)


                    company_name = address_block_match.group(1).strip() if address_block_match else None
                    invoice_date = invoice_date_match.group(1) if invoice_date_match else None
                    name = name_match.group(1) if name_match else None
                    address = address_match.group(1).strip() if address_match else None
                    description = description_match.group(1) if description_match else None


                    amounts = re.findall(r'-?\d+\.\d+', text)
                    amounts = [float(amount) for amount in amounts if float(amount) != 0.0]
                    final_amount_due = amounts[-1] if amounts else None

                    if company_name!=None: inv_title = company_name
                    if invoice_no!= None: inv_no = invoice_no
                    if name!= None: inv_name = name
                    if address!= None: inv_address = address
                    if final_amount_due!= None: inv_amount = final_amount_due
                    if description!=None: inv_content = description


                #check text image
                elif text:
                    text_imagepage.append(num)
            if(page.images) and num not in imagepage:
                imagepage.append(num)

        #Blank
        all_pages = set(range(number_of_pages))
        known_pages = set(textpage) | set(imagepage) | set(invoicepage) | set(text_imagepage)
        blankpage = sorted(all_pages - known_pages)
    
#Print data
        # File information
        col1, col2, col3, col4, col5, col6 = st.columns(6)

        with col1:
            st.markdown("**Total Pages**")
            st.write(number_of_pages)

        with col3:
            st.markdown("**Blank Pages**")
            st.write(", ".join(map(str, blankpage)))
            

        with col4:
            st.markdown("**Image Pages**")
            st.write(", ".join(map(str, imagepage)))
            

        with col5:
            st.markdown("**Text Pages**")
            st.write(", ".join(map(str, textpage)))
            

        with col6:
            st.markdown("**Invoice Pages**")
            st.write(", ".join(map(str, invoicepage)))
           
        with col2:
            st.markdown("**Scanned Pages**")
            st.write(", ".join(map(str, text_imagepage)))

        # Details Extracted From Invoices
        st.subheader("Details Extracted From Invoices")

        invoice_data = {
            "S.No": [1],
            "Invoice No.": [inv_no],
            "Date": [inv_date],
            "Title": [inv_title],
            "Name": [inv_name],
            "Address": [inv_address],
            "Content": [inv_content],
            "Amount": [inv_amount]
        }

        invoice_df = pd.DataFrame(invoice_data)
        st.table(invoice_df)




