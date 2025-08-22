from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
import os
from datetime import datetime, timedelta
from decimal import Decimal

class PagarePDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configurar estilos personalizados para el pagaré"""
        # Estilo para el título principal
        self.styles.add(ParagraphStyle(
            name='TituloPrincipal',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=HexColor('#2c3e50'),
            fontName='Helvetica-Bold'
        ))
        
        # Estilo para subtítulos
        self.styles.add(ParagraphStyle(
            name='Subtitulo',
            parent=self.styles['Heading2'],
            fontSize=18,
            spaceAfter=15,
            alignment=TA_CENTER,
            textColor=HexColor('#34495e'),
            fontName='Helvetica-Bold'
        ))
        
        # Estilo para encabezados de sección
        self.styles.add(ParagraphStyle(
            name='Seccion',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=10,
            spaceBefore=15,
            textColor=HexColor('#3498db'),
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=HexColor('#3498db'),
            borderPadding=5,
            backColor=HexColor('#ecf0f1')
        ))
        
        # Estilo para texto normal
        self.styles.add(ParagraphStyle(
            name='TextoNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            textColor=HexColor('#2c3e50'),
            fontName='Helvetica'
        ))
        
        # Estilo para etiquetas de información
        self.styles.add(ParagraphStyle(
            name='Etiqueta',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            textColor=HexColor('#2c3e50'),
            fontName='Helvetica-Bold'
        ))
        
        # Estilo para valores
        self.styles.add(ParagraphStyle(
            name='Valor',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            textColor=HexColor('#27ae60'),
            fontName='Helvetica'
        ))
        
        # Estilo para condiciones
        self.styles.add(ParagraphStyle(
            name='Condicion',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            textColor=HexColor('#856404'),
            fontName='Helvetica',
            leftIndent=20
        ))
    
    def generar_pagare_pdf(self, prestamo, cliente, output_path):
        """Generar pagaré en formato PDF"""
        try:
            # Crear el documento PDF
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=0.5*inch,
                leftMargin=0.5*inch,
                topMargin=0.5*inch,
                bottomMargin=0.5*inch
            )
            
            # Lista de elementos del PDF
            story = []
            
            # Título principal
            story.append(Paragraph("📄 PAGARÉ GENERADO", self.styles['TituloPrincipal']))
            story.append(Paragraph("PAGARÉ DE PRÉSTAMO PERSONAL", self.styles['Subtitulo']))
            story.append(Spacer(1, 20))
            
            # Información del préstamo
            story.append(Paragraph("📋 INFORMACIÓN DEL PRÉSTAMO", self.styles['Seccion']))
            
            # Tabla de información del préstamo
            prestamo_data = [
                ['Número de Préstamo:', f"#{prestamo.id}"],
                ['Fecha de Emisión:', prestamo.fecha_inicio.strftime('%d/%m/%Y')],
                ['Fecha de Vencimiento:', (prestamo.fecha_inicio + timedelta(days=prestamo.plazo_dias)).strftime('%d/%m/%Y')],
                ['Monto Solicitado:', f"${prestamo.monto:.2f}"],
                ['Plazo:', f"{prestamo.plazo_dias} días"],
                ['Tasa de Interés:', f"{prestamo.tasa_interes:.1f}% anual"],
                ['Tipo de Interés:', prestamo.tipo_interes.title()],
                ['Cuota Diaria:', f"${prestamo.calcular_cuota_diaria():.2f}"],
                ['Total de Intereses:', f"${prestamo.calcular_interes_total():.2f}"],
                ['Total a Pagar:', f"${prestamo.calcular_monto_total():.2f}"]
            ]
            
            prestamo_table = Table(prestamo_data, colWidths=[2.5*inch, 3*inch])
            prestamo_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), HexColor('#f8f9fa')),
                ('TEXTCOLOR', (0, 0), (0, -1), HexColor('#2c3e50')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, HexColor('#dee2e6')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            story.append(prestamo_table)
            story.append(Spacer(1, 20))
            
            # Información del cliente
            story.append(Paragraph("👤 DATOS DEL CLIENTE", self.styles['Seccion']))
            
            cliente_data = [
                ['Nombre Completo:', f"{cliente.nombre} {cliente.apellido}"],
                ['DNI:', cliente.dni],
                ['Teléfono:', cliente.telefono],
                ['Email:', cliente.email or 'No especificado']
            ]
            
            cliente_table = Table(cliente_data, colWidths=[2.5*inch, 3*inch])
            cliente_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), HexColor('#e8f5e8')),
                ('TEXTCOLOR', (0, 0), (0, -1), HexColor('#2c3e50')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, HexColor('#a8e6cf')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            story.append(cliente_table)
            story.append(Spacer(1, 20))
            
            # Condiciones del préstamo
            story.append(Paragraph("📝 CONDICIONES DEL PRÉSTAMO", self.styles['Seccion']))
            
            condiciones = [
                f"• El cliente se compromete a pagar una cuota diaria de <b>${prestamo.calcular_cuota_diaria():.2f}</b>",
                f"• El préstamo será pagado en <b>{prestamo.plazo_dias} días</b>",
                "• En caso de mora, se aplicarán intereses adicionales según la tasa establecida",
                "• El préstamo debe ser cancelado en su totalidad al vencimiento",
                "• Cualquier consulta contactar al prestamista"
            ]
            
            for condicion in condiciones:
                story.append(Paragraph(condicion, self.styles['Condicion']))
            
            story.append(Spacer(1, 20))
            
            # Sección de firma
            story.append(Paragraph("✍️ FIRMA DEL CLIENTE", self.styles['Seccion']))
            story.append(Paragraph("Firma en el recuadro de abajo para confirmar tu compromiso de pago:", self.styles['TextoNormal']))
            story.append(Spacer(1, 30))
            
            # Línea para firma
            story.append(Paragraph("_" * 50, self.styles['TextoNormal']))
            story.append(Spacer(1, 10))
            
            # Información del cliente para firma
            story.append(Paragraph(f"{cliente.nombre} {cliente.apellido}", self.styles['Etiqueta']))
            story.append(Paragraph(f"DNI: {cliente.dni} | Teléfono: {cliente.telefono}", self.styles['TextoNormal']))
            story.append(Spacer(1, 20))
            
            # Información del prestamista
            story.append(Paragraph("Prestamista: Sistema de Préstamos", self.styles['TextoNormal']))
            story.append(Paragraph(f"Fecha de Generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}", self.styles['TextoNormal']))
            
            # Construir el PDF
            doc.build(story)
            
            return True, "Pagaré generado exitosamente"
            
        except Exception as e:
            return False, f"Error al generar PDF: {str(e)}"
    
    def generar_pagare_con_firma_pdf(self, prestamo, cliente, firma_path, output_path):
        """Generar pagaré con firma digital en formato PDF"""
        try:
            # Crear el documento PDF
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=0.5*inch,
                leftMargin=0.5*inch,
                topMargin=0.5*inch,
                bottomMargin=0.5*inch
            )
            
            # Lista de elementos del PDF
            story = []
            
            # Título principal
            story.append(Paragraph("📄 PAGARÉ FIRMADO", self.styles['TituloPrincipal']))
            story.append(Paragraph("PAGARÉ DE PRÉSTAMO PERSONAL", self.styles['Subtitulo']))
            story.append(Spacer(1, 20))
            
            # Información del préstamo
            story.append(Paragraph("📋 INFORMACIÓN DEL PRÉSTAMO", self.styles['Seccion']))
            
            # Tabla de información del préstamo
            prestamo_data = [
                ['Número de Préstamo:', f"#{prestamo.id}"],
                ['Fecha de Emisión:', prestamo.fecha_inicio.strftime('%d/%m/%Y')],
                ['Fecha de Vencimiento:', (prestamo.fecha_inicio + timedelta(days=prestamo.plazo_dias)).strftime('%d/%m/%Y')],
                ['Monto Solicitado:', f"${prestamo.monto:.2f}"],
                ['Plazo:', f"{prestamo.plazo_dias} días"],
                ['Tasa de Interés:', f"{prestamo.tasa_interes:.1f}% anual"],
                ['Tipo de Interés:', prestamo.tipo_interes.title()],
                ['Cuota Diaria:', f"${prestamo.calcular_cuota_diaria():.2f}"],
                ['Total de Intereses:', f"${prestamo.calcular_interes_total():.2f}"],
                ['Total a Pagar:', f"${prestamo.calcular_monto_total():.2f}"]
            ]
            
            prestamo_table = Table(prestamo_data, colWidths=[2.5*inch, 3*inch])
            prestamo_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), HexColor('#f8f9fa')),
                ('TEXTCOLOR', (0, 0), (0, -1), HexColor('#2c3e50')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, HexColor('#dee2e6')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            story.append(prestamo_table)
            story.append(Spacer(1, 20))
            
            # Información del cliente
            story.append(Paragraph("👤 DATOS DEL CLIENTE", self.styles['Seccion']))
            
            cliente_data = [
                ['Nombre Completo:', f"{cliente.nombre} {cliente.apellido}"],
                ['DNI:', cliente.dni],
                ['Teléfono:', cliente.telefono],
                ['Email:', cliente.email or 'No especificado']
            ]
            
            cliente_table = Table(cliente_data, colWidths=[2.5*inch, 3*inch])
            cliente_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), HexColor('#e8f5e8')),
                ('TEXTCOLOR', (0, 0), (0, -1), HexColor('#2c3e50')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, HexColor('#a8e6cf')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            story.append(cliente_table)
            story.append(Spacer(1, 20))
            
            # Condiciones del préstamo
            story.append(Paragraph("📝 CONDICIONES DEL PRÉSTAMO", self.styles['Seccion']))
            
            condiciones = [
                f"• El cliente se compromete a pagar una cuota diaria de <b>${prestamo.calcular_cuota_diaria():.2f}</b>",
                f"• El préstamo será pagado en <b>{prestamo.plazo_dias} días</b>",
                "• En caso de mora, se aplicarán intereses adicionales según la tasa establecida",
                "• El préstamo debe ser cancelado en su totalidad al vencimiento",
                "• Cualquier consulta contactar al prestamista"
            ]
            
            for condicion in condiciones:
                story.append(Paragraph(condicion, self.styles['Condicion']))
            
            story.append(Spacer(1, 20))
            
            # Sección de firma digital
            story.append(Paragraph("✍️ FIRMA DIGITAL DEL CLIENTE", self.styles['Seccion']))
            
            # Agregar la imagen de la firma si existe
            if firma_path and os.path.exists(firma_path):
                try:
                    firma_img = Image(firma_path, width=3*inch, height=1.5*inch)
                    story.append(firma_img)
                    story.append(Spacer(1, 10))
                    story.append(Paragraph("✅ Firma digital registrada", self.styles['Valor']))
                except Exception as e:
                    story.append(Paragraph("⚠️ Error al cargar firma digital", self.styles['TextoNormal']))
            else:
                story.append(Paragraph("📝 Firma pendiente - Firmar en el sistema", self.styles['TextoNormal']))
            
            story.append(Spacer(1, 10))
            
            # Información del cliente para firma
            story.append(Paragraph(f"{cliente.nombre} {cliente.apellido}", self.styles['Etiqueta']))
            story.append(Paragraph(f"DNI: {cliente.dni} | Teléfono: {cliente.telefono}", self.styles['TextoNormal']))
            story.append(Spacer(1, 20))
            
            # Información del prestamista
            story.append(Paragraph("Prestamista: Sistema de Préstamos", self.styles['TextoNormal']))
            story.append(Paragraph(f"Fecha de Generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}", self.styles['TextoNormal']))
            
            # Construir el PDF
            doc.build(story)
            
            return True, "Pagaré con firma generado exitosamente"
            
        except Exception as e:
            return False, f"Error al generar PDF con firma: {str(e)}"
