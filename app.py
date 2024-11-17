import streamlit as st
from fpdf import FPDF
from datetime import datetime
from PIL import Image as PILImage

class PDF(FPDF):
    def header(self):
        if hasattr(self, 'author_name') and self.author_name:
            self.set_font(family='Arial', style='', size=10)
            self.cell(w=0, h=10, txt=f"Autor: {self.author_name}", border=0, ln=0, align='L')

        if hasattr(self, 'logo_path') and self.logo_path:
            self.image(self.logo_path, x=self.w - 40, y=8, w=30)

        self.ln(6)  # Ajuste de espaciado después del encabezado

    def footer(self):
        self.set_y(-15)
        self.set_font(family='Arial', style='I', size=8)
        self.cell(w=0, h=10, txt=f'Página {self.page_no()}', border=0, align='C')

    def title_section(self, title, font='Arial', size=16):
        self.set_font(font, style='B', size=size)
        self.cell(w=0, h=12, txt=title, border=0, ln=1, align='C')
        self.ln(4)  # Espacio reducido después del título

    def task_title(self, title, font='Arial', size=14):
        self.set_font(font, style='B', size=size)
        self.cell(w=0, h=8, txt=title, border=0, ln=1, align='L')
        self.ln(2)  # Ajuste de espaciado después del título de tarea

    def task_body(self, body, font='Arial', size=12):
        self.set_font(font, style='', size=size)
        self.multi_cell(w=0, h=6, txt=body, align='J')
        self.ln(2)  # Espacio pequeño entre párrafos

    def insert_image(self, image_path, width=100):
        # Obtener el tamaño original de la imagen
        with PILImage.open(image_path) as img:
            img_width, img_height = img.size

        # Ajustar la altura proporcionalmente al ancho especificado
        if width:
            img_height = (width / img_width) * img_height
            img_width = width

        x_position = (self.w - img_width) / 2  # Centrado de la imagen en la página

        # Verifica si la imagen cabe en la página actual, si no, agrega una nueva página
        if self.get_y() + img_height + 20 > self.page_break_trigger:  # +20 para margen
            self.add_page()

        # Añadir la imagen y el espacio después
        self.image(image_path, x=x_position, w=img_width, h=img_height)
        self.ln(img_height + 4)  # Espaciado después de la imagen

    def add_dates(self, creation_date, due_date):
        self.set_font('Arial', '', 10)
        self.cell(0, 10, f"Fecha: {creation_date}", ln=True, align='L')
        self.cell(0, 10, f"Fecha de Entrega: {due_date}", ln=True, align='L')
        self.ln(5)

    def add_links(self, links):
        self.set_font('Arial', 'I', 10)
        for link in links:
            self.cell(0, 10, link, ln=True, link=link)

    def create_pdf(self, filename, document_title, author, tasks, logo_path=None, creation_date=None, due_date=None):
        pdf = PDF()
        pdf.author_name = author
        pdf.logo_path = logo_path
        pdf.document_title = document_title
        pdf.add_page()

        # Título del documento
        pdf.title_section(document_title)

        if creation_date and due_date:
            pdf.add_dates(creation_date, due_date)

        for i, task in enumerate(tasks):
            # Añadir una nueva página antes de cada tarea, pero mantener el título del documento
            if i > 0:
                pdf.add_page()  # Salto de página antes de cada tarea
                pdf.title_section(document_title)  # Título del documento en cada página

            title, body, font, size, image_paths, links = task
            pdf.task_title(title, font, size)

            # Añadir los enlaces después del título
            if links:
                pdf.add_links(links)

            pdf.task_body(body, font, size)

            # Ingresar imágenes de la tarea
            for image in image_paths:
                pdf.insert_image(image)

        pdf.output(filename)

def main():
    st.title("Generador de Tareas en PDF para Profesores")
    st.header("Configuración del Documento")
    
    document_title = st.text_input("Título del Documento", placeholder="Escribe el título del documento aquí...")
    author = st.text_input("Autor", placeholder="Escribe el autor aquí...")
    
    uploaded_logo = st.file_uploader("Sube el logo de la unidad educativa (opcional)", type=["jpg", "png"])
    logo_path = None

    if uploaded_logo:
        logo_path = uploaded_logo.name
        with open(logo_path, "wb") as f:
            f.write(uploaded_logo.getbuffer())

    creation_date = datetime.now().strftime("%d/%m/%Y")
    due_date = st.date_input("Fecha de Entrega")
    
    st.header("Tareas del Documento")
    tasks = []
    
    task_count = st.number_input("Número de tareas", min_value=1, max_value=10, value=1)
    
    for i in range(task_count):
        st.subheader(f"Tarea {i+1}")
        title = st.text_input(f"Título de la Tarea {i+1}", placeholder=f"Escribe el título de la tarea {i+1}...")
        body = st.text_area(f"Descripción de la Tarea {i+1}", placeholder=f"Escribe el cuerpo de la tarea {i+1}...")
        font = st.selectbox(f"Fuente de la Tarea {i+1}", ['Arial', 'Courier', 'Times'])
        size = st.slider(f"Tamaño de fuente de la Tarea {i+1}", 10, 16, 12)
        
        uploaded_images = st.file_uploader(f"Sube imágenes para la tarea {i+1} (opcional)", type=["jpg", "png"], accept_multiple_files=True)
        image_paths = []
        
        if uploaded_images:
            for image in uploaded_images:
                image_path = image.name
                with open(image_path, "wb") as f:
                    f.write(image.getbuffer())
                image_paths.append(image_path)
        
        # Pide el número de enlaces a agregar
        link_count = st.number_input(f"Número de enlaces para la tarea {i+1}", min_value=0, max_value=5, value=0)
        links = []
        
        for j in range(link_count):
            link = st.text_input(f"Enlace {j+1} para la tarea {i+1}", placeholder=f"Escribe el enlace {j+1}...")
            if link:
                links.append(link)
        
        tasks.append((title, body, font, size, image_paths, links))

    if st.button("Generar PDF"):
        pdf = PDF()
        pdf.create_pdf(
            filename="Documento_Tareas.pdf", 
            document_title=document_title, 
            author=author, 
            tasks=tasks, 
            logo_path=logo_path, 
            creation_date=creation_date, 
            due_date=due_date.strftime("%d/%m/%Y")
        )

        with open("Documento_Tareas.pdf", "rb") as pdf_file:
            PDFbyte = pdf_file.read()

        st.download_button(
            label="Descargar PDF",
            data=PDFbyte,
            file_name="Documento_Tareas.pdf",
            mime="application/pdf"
        )

if __name__ == "__main__":
    main()
