from fpdf import FPDF

class GenerateContract(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 12)
        self.cell(0, 10, "Contrato de Prestação de Serviços", align="C")
        self.ln(10)

def generate_contract_pdf(name: str, email: str, number: str, address: str) -> str:
    """Generate a PDF contract locally with the provided user data"""
    pdf = GenerateContract()
    pdf.add_page()
    pdf.set_font('Helvetica', size=11)

    text_contract = (
        f"Pelo presente instrumento, de um lado o Prestador, e de outro lado o Sr(a). {name}, "
        f"portador do e-mail {email}, telefone {number} e residente no endereço {address}, "
        "estabelecem o presente contrato de prestação de serviços tecnológicos..."
    )

    pdf.multi_cell(0, 10, text=text_contract)

    safe_name = name.replace(" ", "_").replace("/", "_").replace("\\", "-")
    output_path = f"contratos/contrato_{safe_name}.pdf"
    pdf.output(output_path)
    return output_path