import io
import zipfile
from django.shortcuts import render
from django.http import HttpResponse, Http404, JsonResponse
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from PIL import Image

TOOLS = {
    "merge": {"title": "Merge PDF", "icon": "fa-object-group", "desc": "Combine multiple PDFs into one document seamlessly.", "cat": "organize"},
    "split": {"title": "Split PDF", "icon": "fa-scissors", "desc": "Extract separate pages or split a whole set of documents.", "cat": "organize"},
    "remove-pages": {"title": "Remove Pages", "icon": "fa-trash", "desc": "Delete unwanted individual pages from your PDF file.", "cat": "organize"},
    "extract-pages": {"title": "Extract Pages", "icon": "fa-file-export", "desc": "Get specific pages out of your PDF effortlessly.", "cat": "organize"},
    "organize": {"title": "Organize PDF", "icon": "fa-folder-tree", "desc": "Sort, reorder, and shuffle pages inside your document.", "cat": "organize"},
    "scan-to-pdf": {"title": "Scan to PDF", "icon": "fa-camera", "desc": "Capture paper documents directly into digital high-res PDFs.", "cat": "organize"},
    
    "compress": {"title": "Compress PDF", "icon": "fa-compress", "desc": "Reduce your PDF file size without compromising quality.", "cat": "optimize"},
    "repair": {"title": "Repair PDF", "icon": "fa-wrench", "desc": "Fix corrupted, damaged, or unreadable PDF files.", "cat": "optimize"},
    "ocr": {"title": "OCR PDF", "icon": "fa-font", "desc": "Convert scanned image PDFs into searchable text documents.", "cat": "optimize"},
    
    "jpg-to-pdf": {"title": "JPG to PDF", "icon": "fa-image", "desc": "Turn your PNG or JPG images into standardized PDF files.", "cat": "convert_to"},
    "word-to-pdf": {"title": "WORD to PDF", "icon": "fa-file-word", "desc": "Convert DOC and DOCX text files cleanly into PDFs.", "cat": "convert_to"},
    "powerpoint-to-pdf": {"title": "POWERPOINT to PDF", "icon": "fa-file-powerpoint", "desc": "Transform PPT presentation slides into professional PDFs.", "cat": "convert_to"},
    "excel-to-pdf": {"title": "EXCEL to PDF", "icon": "fa-file-excel", "desc": "Convert XLSX spreadsheets cleanly into PDF tables.", "cat": "convert_to"},
    "html-to-pdf": {"title": "HTML to PDF", "icon": "fa-code", "desc": "Save live web pages or static code snippets as PDFs.", "cat": "convert_to"},

    "pdf-to-jpg": {"title": "PDF to JPG", "icon": "fa-file-image", "desc": "Export every individual PDF page as high-res JPG images.", "cat": "convert_from"},
    "pdf-to-word": {"title": "PDF to WORD", "icon": "fa-file-word", "desc": "Turn static PDFs into fully editable Word documents.", "cat": "convert_from"},
    "pdf-to-powerpoint": {"title": "PDF to POWERPOINT", "icon": "fa-file-powerpoint", "desc": "Convert PDFs back into editable presentation slides.", "cat": "convert_from"},
    "pdf-to-excel": {"title": "PDF to EXCEL", "icon": "fa-file-excel", "desc": "Extract complex raw tables directly into Excel sheets.", "cat": "convert_from"},
    "pdf-to-pdfa": {"title": "PDF to PDF/A", "icon": "fa-box-archive", "desc": "Convert files into ISO-compliant long-term archive formats.", "cat": "convert_from"},

    "rotate": {"title": "Rotate PDF", "icon": "fa-rotate", "desc": "Rotate individual or all pages clockwise or anti-clockwise.", "cat": "edit"},
    "add-page-numbers": {"title": "Add Page Numbers", "icon": "fa-list-ol", "desc": "Stamp professional pagination sequences onto your pages.", "cat": "edit"},
    "add-watermark": {"title": "Add Watermark", "icon": "fa-stamp", "desc": "Protect intellectual property with custom text/image stamps.", "cat": "edit"},
    "crop": {"title": "Crop PDF", "icon": "fa-crop-simple", "desc": "Trim unwanted margins or whitespace off document boundaries.", "cat": "edit"},
    "edit-pdf": {"title": "Edit PDF", "icon": "fa-pen-to-square", "desc": "Annotate, draw, or add text layers directly over the PDF.", "cat": "edit"},

    "unlock": {"title": "Unlock PDF", "icon": "fa-lock-open", "desc": "Strip away known passwords to make documents fully accessible.", "cat": "security"},
    "protect": {"title": "Protect PDF", "icon": "fa-lock", "desc": "Secure sensitive documents with strong encryption codes.", "cat": "security"},
    "sign": {"title": "Sign PDF", "icon": "fa-signature", "desc": "Draw or digitally attach your secure signature to documents.", "cat": "security"},
    "redact": {"title": "Redact PDF", "icon": "fa-eye-slash", "desc": "Permanently blackout confidential words or secret data.", "cat": "security"},
    "compare": {"title": "Compare PDF", "icon": "fa-code-compare", "desc": "Run side-by-side differentials between two document versions.", "cat": "security"},

    "ai-summarizer": {"title": "AI Summarizer", "icon": "fa-robot", "desc": "Condense massive reading materials using smart text analysis.", "cat": "intelligence"},
    "translate": {"title": "Translate PDF", "icon": "fa-language", "desc": "Translate document content instantly across multiple languages.", "cat": "intelligence"},
    "pdf-to-markdown": {"title": "PDF to Markdown", "icon": "fa-hashtag", "desc": "Extract formatted content cleanly into Markdown syntax.", "cat": "intelligence"}
}


def home(request):
    return render(request, 'index.html', {'tools': TOOLS})


def tool_detail(request, tool_name):
    if tool_name not in TOOLS:
        raise Http404("Requested tool configuration does not exist.")
    return render(request, 'tool.html', {'tool': TOOLS[tool_name], 'tool_name': tool_name})


def process_pdf(request, tool_name):
    if tool_name not in TOOLS:
        return JsonResponse({'error': 'Invalid tool specified'}, status=400)

    if request.method != 'POST':
        return render(request, 'tool.html', {'tool': TOOLS[tool_name], 'tool_name': tool_name})

    files = request.FILES.getlist('pdf_files')
    if not files:
        return HttpResponse("Please upload at least one file.", status=400)

    try:
        # ========== MERGE ==========
        if tool_name == 'merge':
            merger = PdfMerger()
            for f in files:
                merger.append(f)
            output = io.BytesIO()
            merger.write(output)
            merger.close()
            output.seek(0)
            response = HttpResponse(output.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="merged.pdf"'
            return response

        # ========== ROTATE ==========
        elif tool_name == 'rotate':
            reader = PdfReader(files[0])
            writer = PdfWriter()
            for page in reader.pages:
                page.rotate(90)
                writer.add_page(page)
            output = io.BytesIO()
            writer.write(output)
            output.seek(0)
            response = HttpResponse(output.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="rotated.pdf"'
            return response

        # ========== SPLIT (each page as separate PDF inside ZIP) ==========
        elif tool_name == 'split':
            reader = PdfReader(files[0])
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                for i, page in enumerate(reader.pages):
                    writer = PdfWriter()
                    writer.add_page(page)
                    page_buffer = io.BytesIO()
                    writer.write(page_buffer)
                    page_buffer.seek(0)
                    zip_file.writestr(f"page_{i+1}.pdf", page_buffer.read())
            zip_buffer.seek(0)
            response = HttpResponse(zip_buffer.read(), content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="split_pages.zip"'
            return response

        # ========== EXTRACT PAGES (first half as example) ==========
        elif tool_name == 'extract-pages':
            reader = PdfReader(files[0])
            writer = PdfWriter()
            total = len(reader.pages)
            # Extract first half of pages
            for i in range(max(1, total // 2)):
                writer.add_page(reader.pages[i])
            output = io.BytesIO()
            writer.write(output)
            output.seek(0)
            response = HttpResponse(output.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="extracted_pages.pdf"'
            return response

        # ========== REMOVE PAGES (remove last page as example) ==========
        elif tool_name == 'remove-pages':
            reader = PdfReader(files[0])
            writer = PdfWriter()
            if len(reader.pages) <= 1:
                return HttpResponse("PDF has only 1 page. Cannot remove.", status=400)
            for i in range(len(reader.pages) - 1):  # remove last page
                writer.add_page(reader.pages[i])
            output = io.BytesIO()
            writer.write(output)
            output.seek(0)
            response = HttpResponse(output.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="pages_removed.pdf"'
            return response

        # ========== ORGANIZE (reverse order) ==========
        elif tool_name == 'organize':
            reader = PdfReader(files[0])
            writer = PdfWriter()
            for page in reversed(reader.pages):
                writer.add_page(page)
            output = io.BytesIO()
            writer.write(output)
            output.seek(0)
            response = HttpResponse(output.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="organized.pdf"'
            return response

        # ========== PROTECT (password = 1234) ==========
        elif tool_name == 'protect':
            reader = PdfReader(files[0])
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            writer.encrypt("1234")  # default password
            output = io.BytesIO()
            writer.write(output)
            output.seek(0)
            response = HttpResponse(output.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="protected.pdf"'
            return response

        # ========== UNLOCK (try empty password) ==========
        elif tool_name == 'unlock':
            try:
                reader = PdfReader(files[0])
                if reader.is_encrypted:
                    reader.decrypt("")  # try empty password
                writer = PdfWriter()
                for page in reader.pages:
                    writer.add_page(page)
                output = io.BytesIO()
                writer.write(output)
                output.seek(0)
                response = HttpResponse(output.read(), content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="unlocked.pdf"'
                return response
            except Exception:
                return HttpResponse("Could not unlock. Password protected with unknown password.", status=400)

        # ========== ADD PAGE NUMBERS ==========
        elif tool_name == 'add-page-numbers':
            reader = PdfReader(files[0])
            writer = PdfWriter()
            for i, page in enumerate(reader.pages):
                packet = io.BytesIO()
                can = canvas.Canvas(packet, pagesize=letter)
                can.setFont("Helvetica", 10)
                can.drawCentredString(letter[0]/2, 30, f"Page {i+1}")
                can.save()
                packet.seek(0)
                watermark = PdfReader(packet)
                page.merge_page(watermark.pages[0])
                writer.add_page(page)
            output = io.BytesIO()
            writer.write(output)
            output.seek(0)
            response = HttpResponse(output.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="numbered.pdf"'
            return response

        # ========== ADD WATERMARK ==========
        elif tool_name == 'add-watermark':
            reader = PdfReader(files[0])
            writer = PdfWriter()
            for page in reader.pages:
                packet = io.BytesIO()
                can = canvas.Canvas(packet, pagesize=letter)
                can.setFont("Helvetica", 40)
                can.setFillColorRGB(0.6, 0.6, 0.6, alpha=0.3)
                can.saveState()
                can.translate(300, 400)
                can.rotate(45)
                can.drawCentredString(0, 0, "CONFIDENTIAL")
                can.restoreState()
                can.save()
                packet.seek(0)
                watermark = PdfReader(packet)
                page.merge_page(watermark.pages[0])
                writer.add_page(page)
            output = io.BytesIO()
            writer.write(output)
            output.seek(0)
            response = HttpResponse(output.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="watermarked.pdf"'
            return response

        # ========== JPG TO PDF ==========
        elif tool_name == 'jpg-to-pdf':
            images = []
            for f in files:
                img = Image.open(f).convert("RGB")
                images.append(img)
            if not images:
                return HttpResponse("No valid images found.", status=400)
            output = io.BytesIO()
            images[0].save(output, format="PDF", save_all=True, append_images=images[1:])
            output.seek(0)
            response = HttpResponse(output.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="images_to_pdf.pdf"'
            return response

        # ========== BASIC COMPRESS ==========
        elif tool_name == 'compress':
            reader = PdfReader(files[0])
            writer = PdfWriter()
            for page in reader.pages:
                page.compress_content_streams()
                writer.add_page(page)
            output = io.BytesIO()
            writer.write(output)
            output.seek(0)
            response = HttpResponse(output.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="compressed.pdf"'
            return response

        # Baaki tools ke liye message
        else:
            return HttpResponse(
                f"Tool '{TOOLS[tool_name]['title']}' is coming soon. Currently working tools: Merge, Split, Rotate, Protect, Watermark, Page Numbers, JPG to PDF, Compress.",
                content_type="text/plain"
            )

    except Exception as e:
        return HttpResponse(f"Error processing file: {str(e)}", status=500)
