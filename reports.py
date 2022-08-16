from fpdf import FPDF
import datetime
import dropbox
from config import ACCESS_TOKEN

def gerar_nome_data_rodape():
    today = datetime.datetime.now()
    day2 = today.timestamp()
    day_fromtmsp = datetime.datetime.fromtimestamp(day2)
    name_file = day_fromtmsp.strftime("%d/%m/%Y - %H:%M")
    return name_file

def gerar_nome_data_arquivo():
    today = datetime.datetime.now()
    day2 = today.timestamp()
    day_fromtmsp = datetime.datetime.fromtimestamp(day2)
    name_file = day_fromtmsp.strftime("%Y_%m_%d_%H_%M_%S_%f")
    return name_file


    

class PDF(FPDF):

    
        # def header(self):
    #     # Logo
    #     self.image('logo_pb.png', 10, 8, 33)
    #     # Arial bold 15
    #     self.set_font('Arial', 'B', 15)
    #     # Move to the right
    #     self.cell(80)
    #     # Title
    #     self.cell(30, 10, 'Title', 1, 0, 'C')
    #     # Line break
    #     self.ln(20)

    # Page footer
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8 )
        # Page number        
        self.cell(0, 10, f'Página: {str(self.page_no())}' , 0, 0, 'L')
        self.cell(0, 10, f'{gerar_nome_data_rodape()}' , 0, 0, 'R')


class TransferData:    

    def __init__(self, access_token):
        self.access_token = access_token

    def upload_file(self, file_from, file_to):
        """upload a file to Dropbox using API v2
        """
        dbx = dropbox.Dropbox(self.access_token)

        with open(file_from, 'rb') as f:
            dbx.files_upload(f.read(), file_to)
        result = dbx.files_get_temporary_link(file_to)
        return result.link

def send_to_server(file_from, file_to):
    access_token = ACCESS_TOKEN
    transferData = TransferData(access_token)
    file_from = file_from
    file_to = file_to  
    transferData.upload_file(file_from, file_to)

    

        