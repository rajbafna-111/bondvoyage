from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa

def render_to_pdf(template_src, context_dict={}):
    """
    Helper function to generate PDF bytes from an HTML template.
    """
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    
    # 1. Use UTF-8 to support Rupee symbol (₹) and other special chars
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    
    # 2. Return the raw value so the View can set headers (Filename, etc.)
    if not pdf.err:
        return result.getvalue()
        
    return None