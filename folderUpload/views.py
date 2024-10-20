import certifi
import ssl
import pandas as pd
from django.http import HttpResponse
from django.core.mail import send_mail
from django.shortcuts import render
from .forms import FileUploadForm
from django.conf import settings


context = ssl.create_default_context(cafile=certifi.where())  #creates ssl context using certifi

def uploadedFile(request):
    if request.method == 'POST': #check if file is submited
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():    #if valid then access particular file from dictionay of filename:file which is stored in FILES
            file = request.FILES['file']  
            if file.name.endswith('.csv'):    #read file if it is csv or excel else return invalid file type
                df = pd.read_csv(file)
            elif file.name.endswith('.xlsx'):
                df = pd.read_excel(file)
            else:
                return render(request, 'upload.html', {'form': form, 'error': 'Invalid file format'})

            summary = generate_custom_summary(df)#generate summary 

            send_summary_email('shreyasmunge@gmail.com', summary) #call function send_summary with two parameters

            return render(request, 'upload.html', {'form': form, 'success': 'Summary emailed successfully!'}) #render html 
    else:
        form = FileUploadForm() #if not Post 

    return render(request, 'upload.html', {'form': form}) #return form again 

def generate_custom_summary(df):
    # Clean the 'Cust State' column by stripping leading/trailing spaces
    df['Cust State'] = df['Cust State'].str.strip().str.upper()  # Convert to uppercase
    
    # Filter for rows with specific states
    filtered_df = df[df['Cust State'].isin(['ARUNACHAL PRADESH', 'JHARKHAND'])]
    
    # Group by 'Cust State' and 'Cust Pin', and count the occurrences
    summary_df = filtered_df.groupby(['Cust State', 'Cust Pin']).size().reset_index(name='DPD')
    
    # Further filter the summary to only include specific Cust Pins
    specific_pins = ['791121', '791112', '816101', '816108']
    filtered_summary_df = summary_df[summary_df['Cust Pin'].astype(str).isin(specific_pins)]
    
    # Format the summary string with clearer spacing
    summary_lines = [
        f"{row['Cust State']: <20} {row['Cust Pin']: <10} {row['DPD']}" 
        for _, row in filtered_summary_df.iterrows()
    ]
    
    # Add a header and a message to provide context
    summary_string = "Summary of the uploaded file:\n\n"
    summary_string += "Cust State         Cust Pin  DPD\n"
    summary_string += "-" * 35 + "\n"  # Adding a separator line
    summary_string += "\n".join(summary_lines) + "\n"  # Join summary lines

    return summary_string




def send_summary_email(recipient, summary): #email sending
    subject = 'tesafjdkajbcakjeiufjsabft'
    html_message = f""" 
    <html>
        <body>
            <h3>Summary</h3>
            <pre>{summary}</pre>
        </body>
    </html>
    """ 
    from_email = settings.EMAIL_HOST_USER

    send_mail(subject, '', from_email, [recipient], fail_silently=False, connection=get_email_backend(),html_message=html_message ) #django has send_mail function with few parameters


def get_email_backend():
    from django.core.mail.backends.smtp import EmailBackend #import smtp email class
    return EmailBackend(
        host=settings.EMAIL_HOST,
        port=settings.EMAIL_PORT,
        username=settings.EMAIL_HOST_USER,
        password=settings.EMAIL_HOST_PASSWORD,
        use_tls=settings.EMAIL_USE_TLS,
        fail_silently=False,
        ssl_context=context  #this ssl context helps smtp to connect with gmail
    )
