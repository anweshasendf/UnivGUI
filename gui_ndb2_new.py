import sys
import pandas as pd
import sqlite3
from nptdms import TdmsFile
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem, QFileDialog, QTabWidget, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QImage, QBrush, QPalette
from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, QThreadPool
from PyQt5.QtCore import QTimer
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QProgressBar
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QScrollArea, QLabel, QFrame
from PyQt5.QtCore import Qt
from reportlab.lib.utils import ImageReader
import PyPDF2
import logger
from pdf2image import convert_from_path
import fitz
import numpy as np
import subprocess
import json
import traceback
import logging
from reportlab.platypus import PageBreak
import io
from PyQt5.QtWidgets import QApplication
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem, QFileDialog, QTabWidget, QMessageBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QProgressDialog
from PyQt5.QtGui import QPixmap, QImage, QBrush, QPalette
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.lib.enums import TA_LEFT
from PyQt5.QtWidgets import QScrollArea, QGroupBox
from reportlab.lib.units import inch
from reportlab.platypus import KeepTogether
from pdf2image import convert_from_path
import io
from PyQt5.QtGui import QImage
import tempfile
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Image
from reportlab.lib.pagesizes import letter
import matplotlib
matplotlib.use('Agg')  # Use the 'Agg' backend which is thread-safe
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from io import BytesIO
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
import re
from PIL import Image as PILImage
from scipy.signal import savgol_filter
from scipy.interpolate import interp1d
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QTextEdit
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import shutil
from PyQt5.QtWidgets import QProgressBar

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Database connection
def check_credentials(user_id, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id=? AND password=?", (user_id, password))
    result = cursor.fetchone()
    conn.close()
    return result

def capture_widget_screenshot(widget: QWidget, filename: str):
    pixmap = widget.grab()
    pixmap.save(filename, "PNG")
    return filename


class PDFGeneratorWorker(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self, output_path, logo_path, data, test_type, neutral_deadband=True, full_efficiency=False, tab_widget = None):
        super().__init__()
        
        print("PDFGeneratorWorker __init__ called")
        print(f"output_path: {output_path}")
        print(f"data keys: {data.keys()}")
        print(f"logo_path: {logo_path}")
        print(f"test_type: {test_type}")
        print(f"tab_widget type: {type(tab_widget)}")
        print(f"tab_widget id: {id(tab_widget)}")
        
        self.output_path = output_path
        self.tab_widget = tab_widget
        
        self.logo_path = logo_path if isinstance(logo_path, str) and os.path.exists(logo_path) else ''

        self.data = data
        self.neutral_deadband = neutral_deadband
        self.full_efficiency = full_efficiency
        self.test_type = test_type
        self.temp_dir = tempfile.mkdtemp()
        self.story = []  # Initialize the story list
        self.styles = getSampleStyleSheet()
        
    def capture_widget_screenshot(widget: QWidget, filename: str):
        pixmap = widget.grab()
        pixmap.save(filename, "PNG")
        return filename

    def run(self):
        try:
            logging.info(f"Starting PDF generation for {self.test_type}")
            self.progress.emit("Initializing PDF generation...")
            
            #pdf_gen = PDFGenerator(self.output_path, self.data, self.temp_dir, self.test_type)
            pdf_gen = PDFGenerator(
            filename=self.output_path,  # Use output_path as filename
            output_path=os.path.dirname(self.output_path),
            data=self.data,
            temp_dir=self.temp_dir,
            test_type=self.test_type
        )
            logging.info("PDFGenerator instance created")
            
            self.progress.emit("Adding cover page...")
            pdf_gen.add_cover_page(self.logo_path)
            logging.info("Cover page added")

            if self.test_type == 'full_efficiency':
                self.progress.emit("Generating Full Efficiency PDF content...")
                self.generate_full_efficiency_pdf(pdf_gen)
            elif self.test_type == 'neutral_deadband':
                self.progress.emit("Generating Neutral Deadband PDF content...")
                self.generate_neutral_deadband_pdf(pdf_gen)
            else:
                raise ValueError(f"Unknown test type: {self.test_type}")

            self.progress.emit("Saving PDF...")
            logging.info("Saving PDF")
            
            pdf_gen.save()
            logging.info("PDF saved successfully")
            #self.progress.emit("PDF generation completed")
            
            
            
            c = canvas.Canvas(self.output_path, pagesize=letter)
            c.drawString(100, 750, f"Test PDF for {self.test_type}")
            c.drawString(100, 700, f"Logo path: {self.logo_path}")
            c.save()
            
            logging.info(f"PDFGeneratorWorker: PDF generated at {self.output_path}")
            self.progress.emit("PDF generation completed")
            self.finished.emit()
            self.finished.emit(self.output_path)
        except Exception as e:
            logging.error(f"Error in PDF generation: {str(e)}")
            logging.error(f"Error type: {type(e).__name__}")
            logging.error(traceback.format_exc())
            self.error.emit(str(e))
        finally:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                
    def add_plots_from_pdf_gen(self, pdf_gen):
        for element in pdf_gen.story:
            if isinstance(element, Image):
                try:
                    # Get the filename from the image path
                    filename = os.path.basename(element._filename)
                    
                    # Add a paragraph with the plot title
                    self.story.append(Paragraph(f"Plot: {filename}", self.styles['Heading2']))
                    
                    # Create a new Image object with the same file path
                    img = Image(element._filename, width=6*inch, height=4*inch)
                    
                    # Add the image to the story
                    self.story.append(img)
                    
                    # Add some space after the image
                    self.story.append(Spacer(1, 12))
                    
                    logging.info(f"Added plot: {filename}")
                except Exception as e:
                    logging.error(f"Error adding plot {filename}: {str(e)}")
            
    def add_tables_to_story(self):
        for tab_name, tab_data in self.data['tables'].items():
            try:
                self.story.append(Paragraph(f"Table: {tab_name}", self.styles['Heading2']))
                
                headers = tab_data['columns']
                data = tab_data['data']
                
                # Calculate available width
                available_width = letter[0] - 1*inch  # Subtract margins
                
                # Calculate column widths
                col_widths = [min(max(len(str(row[i])) for row in data + [headers]) * 0.09 * inch, 1.2*inch) for i in range(len(headers))]
                
                # If total width exceeds available width, adjust proportionally
                total_width = sum(col_widths)
                if total_width > available_width:
                    scale_factor = available_width / total_width
                    col_widths = [width * scale_factor for width in col_widths]
                
                # Wrap long text in headers and data
                wrapped_headers = [Paragraph(str(header), ParagraphStyle('Normal', fontSize=6, leading=7)) for header in headers]
                wrapped_data = [[Paragraph(str(cell), ParagraphStyle('Normal', fontSize=6, leading=7)) for cell in row] for row in data]
                
                table_data = [wrapped_headers] + wrapped_data
                table = Table(table_data, colWidths=col_widths, repeatRows=1)
                
                # Add styling to the table
                style = TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 3),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 6),
                    ('TOPPADDING', (0, 1), (-1, -1), 2),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 2),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black)
                ])
                table.setStyle(style)
                
                self.story.append(table)
                self.story.append(Spacer(1, 12))
            except Exception as e:
                logging.error(f"Error adding table {tab_name}: {str(e)}")

    def add_plots_to_story(self):
        if 'plots' in self.data:
            for plot_name, plot_data in self.data['plots'].items():
                try:
                    self.story.append(Paragraph(f"Plot: {plot_name}", self.styles['Heading2']))
                    
                    logging.info(f"Processing plot: {plot_name}")
                    logging.info(f"Plot data type: {type(plot_data)}")
                    logging.info(f"Plot data: {plot_data}")  # Log the actual plot data
                    
                    if isinstance(plot_data, dict) and 'path' in plot_data:
                        # If plot_data is a dictionary with a 'path' key, use the image file
                        img_path = plot_data['path']
                        img = Image(img_path, width=6*inch, height=4*inch)
                        self.story.append(img)
                    else:
                        img_buffer = BytesIO()
                        fig, ax = plt.subplots(figsize=(8, 6))
                        
                        if isinstance(plot_data, dict):
                            if 'x' in plot_data and 'y' in plot_data:
                                ax.plot(plot_data['x'], plot_data['y'])
                            elif 'data' in plot_data:
                                ax.plot(plot_data['data'])
                            else:
                                for key, value in plot_data.items():
                                    if isinstance(value, (list, tuple)):
                                        ax.plot(value, label=key)
                                ax.legend()
                        elif isinstance(plot_data, (list, tuple)):
                            ax.plot(plot_data)
                        else:
                            ax.text(0.5, 0.5, f"Unexpected plot data type: {type(plot_data)}", ha='center', va='center')
                        
                        ax.set_title(plot_name)
                        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
                        img_buffer.seek(0)
                        img = Image(img_buffer, width=6*inch, height=4*inch)
                        plt.close(fig)
                        
                        self.story.append(img)
                    
                    self.story.append(Spacer(1, 12))
                except Exception as e:
                    logging.error(f"Error adding plot {plot_name}: {str(e)}")
                    logging.error(traceback.format_exc())
                
            
    def add_full_efficiency_content(self, pdf_gen):
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            tab_name = self.tab_widget.tabText(i)

            if tab_name == "Summary":
                self.add_summary_content(pdf_gen, tab)
            elif tab_name == "Results":
                self.add_results_content(pdf_gen, tab)
            elif tab_name == "General Plots":
                self.add_general_plots_content(pdf_gen, tab)
            elif tab_name == "Time Series":
                self.add_time_series_content(pdf_gen, tab)
            elif tab_name == "Plots":
                self.add_plots_content(pdf_gen, tab)
                
    def add_summary_content(self, pdf_gen, summary_data):
    # Add summary content to the PDF
        pdf_gen.add_heading("Summary")
        for key, value in summary_data.items():
            pdf_gen.add_paragraph(f"{key}: {value}")

    def add_results_content(self, pdf_gen, results_path):
        if os.path.exists(results_path):
            df = pd.read_csv(results_path)
            data = [df.columns.tolist()] + df.values.tolist()
            pdf_gen.add_table(data, "Results")
        else:
            pdf_gen.add_paragraph("No results found.")

    def add_general_plots_content(self, pdf_gen, results_path):
        if os.path.exists(results_path):
            df = pd.read_csv(results_path)
            numeric_columns = df.select_dtypes(include=[np.number]).columns

            for column in numeric_columns:
                fig = Figure(figsize=(12, 8))
                ax = fig.add_subplot(111)
                ax.plot(df.index, df[column], label=column)
                
                min_val = df[column].min()
                max_val = df[column].max()
                mean_val = df[column].mean()
                
                ax.axhline(min_val, color='r', linestyle='--', label=f'Min: {min_val:.2f}')
                ax.axhline(max_val, color='g', linestyle='--', label=f'Max: {max_val:.2f}')
                ax.axhline(mean_val, color='b', linestyle='--', label=f'Mean: {mean_val:.2f}')
                
                ax.set_title(f"{column} vs Index")
                ax.set_xlabel("Index")
                ax.set_ylabel(column)
                ax.legend()

                canvas = FigureCanvas(fig)
                canvas.draw()
                buf = io.BytesIO()
                canvas.print_png(buf)
                buf.seek(0)
                pdf_gen.add_image(buf, f"{column} vs Index")

    def add_time_series_content(self, pdf_gen, results_path, all_df):
        try:
            df = pd.read_csv(results_path)
            if 'Time' not in df.columns:
                df['Time'] = df.index

            fig, ax1 = plt.subplots(figsize=(12, 8))

            colors = {'Delta_P': 'red', 'Output_Shaft_Torque': 'blue', 'Swash_Angle': 'green'}

            def find_column(possible_names, dataframes):
                for df in dataframes:
                    for name in possible_names:
                        if name in df.columns:
                            return df, name
                return None, None

            df_delta_p, delta_p_col = find_column(['Delta_P_Bar', 'Mean_delta_P'], [df, all_df])
            if df_delta_p is not None and delta_p_col:
                ax1.set_xlabel('Time')
                ax1.set_ylabel('Delta P (Bar)', color=colors['Delta_P'])
                ax1.plot(df_delta_p.index, df_delta_p[delta_p_col], color=colors['Delta_P'], label='Delta P')
                ax1.tick_params(axis='y', labelcolor=colors['Delta_P'])

            df_torque, torque_col = find_column(['Case_LPM', 'Mean_Case_LPM', 'Mean_output_shaft_tq'], [df, all_df])
            if df_torque is not None and torque_col:
                ax2 = ax1.twinx()
                ax2.set_ylabel('Output Shaft Torque (Nm)', color=colors['Output_Shaft_Torque'])
                ax2.plot(df_torque.index, df_torque[torque_col], color=colors['Output_Shaft_Torque'], label='Output Shaft Torque')
                ax2.tick_params(axis='y', labelcolor=colors['Output_Shaft_Torque'])

            df_angle, swash_angle_col = find_column(['Swashplate angle', 'Angle', 'Swash_Angle'], [df, all_df])
            if df_angle is not None and swash_angle_col:
                ax3 = ax1.twinx()
                ax3.spines['right'].set_position(('axes', 1.1))
                ax3.set_ylabel('Swashplate Angle', color=colors['Swash_Angle'])
                ax3.plot(df_angle.index, df_angle[swash_angle_col], color=colors['Swash_Angle'], label='Swashplate Angle')
                ax3.tick_params(axis='y', labelcolor=colors['Swash_Angle'])

            lines, labels = [], []
            for ax in [ax1, ax2, ax3]:
                if ax and ax.get_legend_handles_labels()[0]:
                    lines.extend(ax.get_legend_handles_labels()[0])
                    labels.extend(ax.get_legend_handles_labels()[1])
            if lines and labels:
                ax1.legend(lines, labels, loc='upper left')

            plt.title('Time Series Plot')

            canvas = FigureCanvas(fig)
            canvas.draw()
            buf = io.BytesIO()
            canvas.print_png(buf)
            buf.seek(0)
            pdf_gen.add_image(buf, "Time Series Plot")

        except Exception as e:
            logging.error(f"Error creating time series plot: {str(e)}")
            pdf_gen.add_paragraph(f"Error creating time series plot: {str(e)}")
            
    def add_plots_content(self, pdf_gen, results_folder):
        for file in os.listdir(results_folder):
            if file.startswith("plot_U") and file.endswith(".png"):
                plot_path = os.path.join(results_folder, file)
                pdf_gen.add_image(plot_path, file)

    # def add_plots_content(self, pdf_gen, tab):
    #     pdf_gen.add_heading("Plots")
        
    #     plot_counter = 0
    #     for i in range(tab.layout().count()):
    #         widget = tab.layout().itemAt(i).widget()
    #         if isinstance(widget, QLabel) and widget.pixmap():
    #             plot_counter += 1
    #             pixmap = widget.pixmap()
    #             image_path = os.path.join(self.temp_dir, f"plot_{plot_counter}.png")
    #             pixmap.save(image_path, "PNG")
    #             pdf_gen.add_image(image_path, f'Plot {plot_counter}')

    def cleanup_temp_dir(self):
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except Exception as e:
                print(f"Error cleaning up temporary directory: {e}")

    def save_plot_as_image(self, fig, filename):
        path = os.path.join(self.temp_dir, filename)
        fig.savefig(path, format='png', dpi=300, bbox_inches='tight')
        return path

    def generate_neutral_deadband_pdf(self, pdf_gen):
        try:
            logging.info("Starting Neutral Deadband PDF generation")
            logging.info(f"Data keys: {self.data.keys()}")
            
            pdf_gen.add_title("HST Neutral Deadband Test Results")
            
            if self.logo_path:
                pdf_gen.add_image(self.logo_path, "Company Logo")

            self.add_results_content_ndb(pdf_gen, self.data['results_path'])
            self.add_plots_content_ndb(pdf_gen, os.path.join(self.data['folder_path'], "results"))
            self.add_general_plots_content_ndb(pdf_gen, self.data['results_path'])
            
            logging.info("Neutral Deadband PDF content added successfully")
        except Exception as e:
            logging.error(f"Error generating Neutral Deadband PDF content: {str(e)}")
            logging.error(traceback.format_exc())
            raise
        
    def add_results_content_ndb(self, pdf_gen, results_path):
        try:
            if os.path.exists(results_path):
                df = pd.read_csv(results_path)
                if not df.empty:
                    data = [df.columns.tolist()] + df.values.tolist()
                    pdf_gen.add_table(data, "Results")
                else:
                    logging.warning("Results data is empty")
                    pdf_gen.add_paragraph("No results data available")
            else:
                logging.warning(f"Results file not found: {results_path}")
                pdf_gen.add_paragraph("Results file not found")
        except Exception as e:
            logging.error(f"Error adding results content: {str(e)}")
            pdf_gen.add_paragraph(f"Error adding results content: {str(e)}")

    def add_plots_content_ndb(self, pdf_gen, results_folder):
        try:
            for file in os.listdir(results_folder):
                if file.startswith("plot_U") and file.endswith(".png"):
                    plot_path = os.path.join(results_folder, file)
                    pdf_gen.add_image(plot_path, file)
        except Exception as e:
            logging.error(f"Error adding plots content: {str(e)}")
            pdf_gen.add_paragraph(f"Error adding plots content: {str(e)}")

    def add_general_plots_content_ndb(self, pdf_gen, results_path):
        try:
            if os.path.exists(results_path):
                df = pd.read_csv(results_path)
                numeric_columns = df.select_dtypes(include=[np.number]).columns

                for column in numeric_columns:
                    fig = Figure(figsize=(12, 8))
                    ax = fig.add_subplot(111)
                    ax.plot(df.index, df[column], label=column)
                    
                    min_val = df[column].min()
                    max_val = df[column].max()
                    mean_val = df[column].mean()
                    
                    ax.axhline(min_val, color='r', linestyle='--', label=f'Min: {min_val:.2f}')
                    ax.axhline(max_val, color='g', linestyle='--', label=f'Max: {max_val:.2f}')
                    ax.axhline(mean_val, color='b', linestyle='--', label=f'Mean: {mean_val:.2f}')
                    
                    ax.set_title(f"{column} vs Index")
                    ax.set_xlabel("Index")
                    ax.set_ylabel(column)
                    ax.legend()

                    canvas = FigureCanvas(fig)
                    canvas.draw()
                    buf = io.BytesIO()
                    canvas.print_png(buf)
                    buf.seek(0)
                    pdf_gen.add_image(buf, f"{column} vs Index")
            else:
                logging.warning(f"Results file not found for general plots: {results_path}")
                pdf_gen.add_paragraph("General plots data not available")
        except Exception as e:
            logging.error(f"Error adding general plots content: {str(e)}")
            pdf_gen.add_paragraph(f"Error adding general plots content: {str(e)}")
                                
    def add_summary_tab_content(self, pdf_gen):
        logging.info("Adding summary tab content")
        pdf_gen.add_heading("Summary")
        
        if 'Summary' in self.data['tables']:
            summary_data = self.data['tables']['Summary']
            for table_name, table_data in summary_data.items():
                pdf_gen.add_table(table_data['data'], table_name)
        
                pdf_gen.add_spacer(0.2 * inch)

            
            for table_name, table_data in summary_data.items():
                logging.info(f"Adding table: {table_name}")
                self.add_table_data_to_pdf(pdf_gen, table_data, table_name)
        else:
            logging.warning("No Summary data found in self.data['tables']")
        
        
        
    def add_plot_to_pdf(self, pdf_gen, plot_data, tab_name, plot_key):
        try:
            if 'path' in plot_data:
                pdf_gen.add_image(plot_data['path'], f"Plot: {plot_key}")
            elif 'figure' in plot_data:
                temp_plot_path = self.save_plot_as_image(plot_data['figure'], f"temp_plot_{tab_name}_{plot_key}.png")
                if temp_plot_path and os.path.exists(temp_plot_path):
                    pdf_gen.add_image(temp_plot_path, f"Plot: {plot_key}")
                else:
                    pdf_gen.add_paragraph(f"Plot image not available for {tab_name} - {plot_key}")
            else:
                pdf_gen.add_paragraph(f"Plot data not available for {tab_name} - {plot_key}")
        except Exception as plot_error:
            pdf_gen.add_paragraph(f"Error processing plot: {str(plot_error)}")

    def add_table_data_to_pdf(self, pdf_gen, table_data, table_name):
        logging.info(f"Adding table data for: {table_name}")
        logging.info(f"Table data type: {type(table_data)}")
        
        if isinstance(table_data, dict) and 'headers' in table_data and 'data' in table_data:
            headers = table_data['headers']
            data = table_data['data']
            
            logging.info(f"Headers: {headers}")
            logging.info(f"Data rows: {len(data)}")
            
            # Create a list of lists for the table
            table_data_list = [headers] + data
            
            # Check if the table has any data
            if len(table_data_list) > 1 and len(table_data_list[0]) > 0:
                # Add the table to the PDF
                pdf_gen.add_table(table_data_list, table_name)
            else:
                logging.warning(f"Table {table_name} is empty, skipping")
        else:
            logging.warning(f"Invalid table data structure for {table_name}")

    def add_plot_to_pdf(self, pdf_gen, plot_data, tab_name, plot_key):
        try:
            if 'path' in plot_data:
                pdf_gen.add_image(plot_data['path'], f"Plot: {plot_key}", f"{tab_name} - {plot_key}")
            elif 'figure' in plot_data:
                temp_plot_path = self.save_plot_as_image(plot_data['figure'], f"temp_plot_{tab_name}_{plot_key}.png")
                if temp_plot_path and os.path.exists(temp_plot_path):
                    pdf_gen.add_image(temp_plot_path, f"Plot: {plot_key}", f"{tab_name} - {plot_key}")
                else:
                    pdf_gen.add_paragraph(f"Plot image not available for {tab_name} - {plot_key}")
            else:
                pdf_gen.add_paragraph(f"Plot data not available for {tab_name} - {plot_key}")
        except Exception as plot_error:
            pdf_gen.add_paragraph(f"Error processing plot: {str(plot_error)}")


    def add_ndb_data(self, pdf_gen, table_data):
        try:
            # Assuming the data is in the first row of the table
            row = table_data['data'][0]
            
            ndb_value = row[9]  # "Zero of NDB lies at" is at index 9
            a1 = float(row[2])
            b1 = float(row[4])
            ndb_value_calc = abs(a1 - b1)
            a_band = row[7]
            b_band = row[8]
            delta_a1 = row[10]
            delta_a2 = row[11]
            delta_b1 = row[12]
            delta_b2 = row[13]
            
            pdf_gen.add_paragraph(f"Zero of NDB lies at: {ndb_value}")
            pdf_gen.add_paragraph(f"NDB Value: {ndb_value_calc:.2f}")
            pdf_gen.add_paragraph(f"A band: {a_band:.2f}")
            pdf_gen.add_paragraph(f"B band: {b_band:.2f}")
            pdf_gen.add_paragraph(f"Delta @ A1: {delta_a1:.2f}")
            pdf_gen.add_paragraph(f"Delta @ A2: {delta_a2:.2f}")
            pdf_gen.add_paragraph(f"Delta @ B1: {delta_b1:.2f}")
            pdf_gen.add_paragraph(f"Delta @ B2: {delta_b2:.2f}")
        except Exception as e:
            pdf_gen.add_paragraph(f"Error processing NDB data: {str(e)}")

    def add_additional_tab_content(self, pdf_gen, tab, tab_name):
        # Add any additional content specific to this tab
        if tab_name == "Results":
            self.add_results_tab_content(pdf_gen, tab)
        elif tab_name == "Plots":
            self.add_plots_tab_content(pdf_gen, tab)
            

    def generate_full_efficiency_pdf(self, pdf_gen):
        try:
            logging.info("Starting Full Efficiency PDF generation")
            logging.info(f"Data keys: {self.data.keys()}")
            
            pdf_gen.add_title("HST Full Efficiency Test Results")
            
            if self.logo_path:
                pdf_gen.add_image(self.logo_path, "Company Logo")

            self.add_results_content(pdf_gen, self.data['results_path'])
            self.add_plots_content(pdf_gen, os.path.join(self.data['folder_path'], "results"))
            self.add_general_plots_content(pdf_gen, self.data['results_path'])
            self.add_time_series_content(pdf_gen, self.data['results_path'], self.data.get('all_df', pd.DataFrame()))
            
            logging.info("Full Efficiency PDF content added successfully")
        except Exception as e:
            logging.error(f"Error generating Full Efficiency PDF content: {str(e)}")
            logging.error(traceback.format_exc())
            raise

    def add_neutral_deadband_tab_content(self, pdf_gen, tab, tab_name):
        # Existing code for adding Neutral Deadband tab content
        if tab_name in self.data['plots']:
                        for plot_key, plot_data in self.data['plots'][tab_name].items():
                            logging.debug(f"Processing plot {plot_key} for tab: {tab_name}")
                            try:
                                # Check if the plot data contains a 'path' or 'figure'
                                if 'path' in plot_data:
                                    plot_path = plot_data['path']
                                    pdf_gen.elements.append(Image(plot_path, width=7*inch, height=5*inch))
                                elif 'figure' in plot_data:
                                    temp_plot_path = self.save_plot_as_image(plot_data['figure'], f"temp_plot_{tab_name}_{plot_key}.png")
                                    if temp_plot_path and os.path.exists(temp_plot_path):
                                        pdf_gen.elements.append(Image(temp_plot_path, width=7*inch, height=5*inch))
                                    else:
                                        logging.warning(f"Temp plot file not found or could not be created for {tab_name} - {plot_key}")
                                        pdf_gen.elements.append(Paragraph(f"Plot image not available for {tab_name} - {plot_key}", pdf_gen.styles['Normal']))
                                else:
                                    logging.warning(f"No 'path' or 'figure' found for plot {plot_key} in tab {tab_name}")
                                    pdf_gen.elements.append(Paragraph(f"Plot data not available for {tab_name} - {plot_key}", pdf_gen.styles['Normal']))
                            except Exception as plot_error:
                                logging.error(f"Error processing plot for tab {tab_name} - {plot_key}: {str(plot_error)}")
                                pdf_gen.elements.append(Paragraph(f"Error processing plot: {str(plot_error)}", pdf_gen.styles['Normal']))
                            
                        # Add NDB value and other new data
                        if tab_name in self.data['tables']:
                            table_data = self.data['tables'][tab_name]
                            ndb_value = table_data['data'][0][9]  # "Zero of NDB lies at" is at index 9
                            pdf_gen.elements.append(Paragraph(f"Zero of NDB lies at: {ndb_value}", pdf_gen.styles['Normal']))
                            
                            # Add new data
                            a1 = float(table_data['data'][0][2])
                            b1 = float(table_data['data'][0][4])
                            ndb_value_calc = abs(a1 - b1)
                            a_band = table_data['data'][0][7]
                            b_band = table_data['data'][0][8]
                            delta_a1 = table_data['data'][0][10]
                            delta_a2 = table_data['data'][0][11]
                            delta_b1 = table_data['data'][0][12]
                            delta_b2 = table_data['data'][0][13]
                            
                            pdf_gen.elements.append(Paragraph(f"NDB Value: {ndb_value_calc:.2f}", pdf_gen.styles['Normal']))
                            pdf_gen.elements.append(Paragraph(f"A band: {a_band:.2f}", pdf_gen.styles['Normal']))
                            pdf_gen.elements.append(Paragraph(f"B band: {b_band:.2f}", pdf_gen.styles['Normal']))
                            pdf_gen.elements.append(Paragraph(f"Delta @ A1: {delta_a1:.2f}", pdf_gen.styles['Normal']))
                            pdf_gen.elements.append(Paragraph(f"Delta @ A2: {delta_a2:.2f}", pdf_gen.styles['Normal']))
                            pdf_gen.elements.append(Paragraph(f"Delta @ B1: {delta_b1:.2f}", pdf_gen.styles['Normal']))
                            pdf_gen.elements.append(Paragraph(f"Delta @ B2: {delta_b2:.2f}", pdf_gen.styles['Normal']))
                            #pdf_gen.elements.append(Paragraph(f"Zero at NDB Value: {ndb_value_calc:.2f}", pdf_gen.styles['Normal']))
                            pdf_gen.elements.append(Spacer(1, 12))
        pdf_gen.add_page()
        pdf_gen.add_title(tab_name)

        table_widgets = tab.findChildren(QTableWidget)
        for table_widget in table_widgets:
            try:
                pdf_gen.add_table(table_widget)
            except Exception as table_error:
                logging.error(f"Error adding table for tab {tab_name}: {str(table_error)}")
                pdf_gen.elements.append(Paragraph(f"Error adding table: {str(table_error)}", pdf_gen.styles['Normal']))
        
        if tab_name in self.data['plots']:
            for plot_key, plot_data in self.data['plots'][tab_name].items():
                self.add_plot_to_pdf(pdf_gen, plot_data, tab_name, plot_key)

        self.add_ndb_data(pdf_gen, tab_name)

    # def add_full_efficiency_summary(self, pdf_gen):
    #     pdf_gen.add_page()
    #     pdf_gen.add_title("Summary")
        
    #     # Check if we have summary data in the self.data dictionary
    #     if 'summary' in self.data:
    #         summary_data = self.data['summary']
    #         if isinstance(summary_data, pd.DataFrame):
    #             pdf_gen.add_table(
    #                 data=summary_data.values.tolist(),
    #                 title="Summary Table",
    #                 headers=summary_data.columns.tolist()
    #             )
    #         elif isinstance(summary_data, dict):
    #             for table_name, table_data in summary_data.items():
    #                 if isinstance(table_data, pd.DataFrame):
    #                     pdf_gen.add_table(
    #                         data=table_data.values.tolist(),
    #                         title=f"Summary: {table_name}",
    #                         headers=table_data.columns.tolist()
    #                     )
    #                 else:
    #                     logging.warning(f"Unexpected data type for summary table {table_name}")
    #         else:
    #             logging.warning("Unexpected data type for summary")
    #     else:
    #         logging.warning("No summary data found")
            
    # def add_full_efficiency_results(self, pdf_gen):
    #     pdf_gen.add_page()
    #     pdf_gen.add_title("Results")
    #     if 'results' in self.data:
    #         results_data = self.data['results']
    #         if isinstance(results_data, pd.DataFrame):
    #             pdf_gen.add_table(
    #                 data=results_data.values.tolist(),
    #                 title="Full Efficiency Results",
    #                 headers=results_data.columns.tolist()
    #             )
    #         else:
    #             logging.warning("Unexpected data type for results")
    #     else:
    #         logging.warning("No results data found")

    # def add_full_efficiency_general_plots(self, pdf_gen):
    #     pdf_gen.add_page()
    #     pdf_gen.add_heading("General Plots")
        
    #     results_path = self.data['results_path']
    #     if os.path.exists(results_path):
    #         df = pd.read_csv(results_path)
    #         numeric_columns = df.select_dtypes(include=[np.number]).columns

    #         for column in numeric_columns:
    #             fig = Figure(figsize=(12, 8))
    #             ax = fig.add_subplot(111)
    #             ax.plot(df.index, df[column], label=column)
                
    #             min_val = df[column].min()
    #             max_val = df[column].max()
    #             mean_val = df[column].mean()
                
    #             ax.axhline(min_val, color='r', linestyle='--', label=f'Min: {min_val:.2f}')
    #             ax.axhline(max_val, color='g', linestyle='--', label=f'Max: {max_val:.2f}')
    #             ax.axhline(mean_val, color='b', linestyle='--', label=f'Mean: {mean_val:.2f}')
                
    #             ax.set_title(f"{column} vs Index")
    #             ax.set_xlabel("Index")
    #             ax.set_ylabel(column)
    #             ax.legend()

    #             plot_path = self.save_plot_as_image(fig, f"general_plot_{column}.png")
    #             pdf_gen.add_plot(plot_path, f"General Plot: {column}")
    #             pdf_gen.add_spacer(0.5 * inch)  # Add some space between plots

    #     else:
    #         pdf_gen.add_paragraph("No general plots available.")
            
    #     if 'general_plots' in self.data:
    #         for plot_name, plot_path in self.data['general_plots'].items():
    #             pdf_gen.add_image(plot_path, f"General Plot: {plot_name}", plot_name)
    #     else:
    #         logging.warning("No general plots found")

    # def add_full_efficiency_time_series(self, pdf_gen): #Had Tab
    #     pdf_gen.add_page()
    #     pdf_gen.add_title("Time Series")
    #     # for canvas in tab.findChildren(FigureCanvas):
    #     #     plot_path = self.save_plot_as_image(canvas.figure, f"time_series_plot_{canvas.figure.number}.png")
    #     #     pdf_gen.add_plot(plot_path, f"Time Series Plot {canvas.figure.number}")
        
    #     if 'time_series' in self.data:
    #         time_series_data = self.data['time_series']
    #         if isinstance(time_series_data, dict):
    #             for plot_name, plot_data in time_series_data.items():
    #                 if 'path' in plot_data:
    #                     pdf_gen.add_image(plot_data['path'], f"Time Series: {plot_name}", plot_name)
    #                 elif 'data' in plot_data:
    #                     # If we have raw data, we might need to generate the plot here
    #                     # This is a placeholder for plot generation logic
    #                     fig = self.create_time_series_tab(plot_data['data'], plot_name)
    #                     plot_path = self.save_plot_as_image(fig, f"time_series_{plot_name}.png")
    #                     pdf_gen.add_image(plot_path, f"Time Series: {plot_name}", plot_name)
    #                 else:   
    #                     logging.warning(f"No valid data found for time series plot: {plot_name}")
    #         else:
    #             logging.warning("Unexpected data type for time series")
    #     else:
    #         logging.warning("No time series data found")


    # def add_full_efficiency_plots(self, pdf_gen):
    #     pdf_gen.add_page()
    #     pdf_gen.add_title("Efficiency Plots")
        
    #     plot_counter = 0
    #     # for label in tab.findChildren(QLabel):
    #     #     if label.pixmap() and not label.pixmap().isNull():
    #     #         plot_counter += 1
    #     #         plot_path = self.save_pixmap_as_image(label.pixmap(), f"efficiency_plot_{plot_counter}.png")
    #     #         pdf_gen.add_plot(plot_path, f"Efficiency Plot {plot_counter}")
    #     #         pdf_gen.add_spacer(0.5 * inch)  # Add some space between plots
        
    #     if 'efficiency_plots' in self.data:
    #         efficiency_plots = self.data['efficiency_plots']
    #         if isinstance(efficiency_plots, dict):
    #             for plot_name, plot_data in efficiency_plots.items():
    #                 if 'path' in plot_data:
    #                     pdf_gen.add_image(plot_data['path'], f"Efficiency Plot: {plot_name}", plot_name)
    #                 elif 'data' in plot_data:
    #                     # If we have raw data, we might need to generate the plot here
    #                     # This is a placeholder for plot generation logic
    #                     fig = self.create_plots_tab(plot_data['data'], plot_name)
    #                     plot_path = self.save_plot_as_image(fig, f"efficiency_{plot_name}.png")
    #                     pdf_gen.add_image(plot_path, f"Efficiency Plot: {plot_name}", plot_name)
    #                 else:
    #                     logging.warning(f"No valid data found for efficiency plot: {plot_name}")
    #         else:
    #             logging.warning("Unexpected data type for efficiency plots")
    #     else:
    #         logging.warning("No efficiency plots data found")

    #     if plot_counter == 0:
    #         pdf_gen.add_paragraph("No efficiency plots available.")
    
    def add_full_efficiency_summary(self, pdf_gen):
        pdf_gen.add_page()
        pdf_gen.add_title("Summary")
        
        summary_tab = self.tab_widget.widget(0)  # Assuming Summary is the first tab
        screenshot_path = capture_widget_screenshot(summary_tab, os.path.join(self.temp_dir, "summary_screenshot.png"))
        pdf_gen.add_image(screenshot_path, "Summary Tab Screenshot", "Summary Tab")

    def add_full_efficiency_results(self, pdf_gen):
        pdf_gen.add_page()
        pdf_gen.add_title("Results")
        
        results_tab = self.tab_widget.widget(1)  # Assuming Results is the second tab
        screenshot_path = capture_widget_screenshot(results_tab, os.path.join(self.temp_dir, "results_screenshot.png"))
        pdf_gen.add_image(screenshot_path, "Results Tab Screenshot", "Results Tab")

    def add_full_efficiency_general_plots(self, pdf_gen):
        pdf_gen.add_page()
        pdf_gen.add_title("General Plots")
        
        general_plots_tab = self.tab_widget.widget(2)  # Assuming General Plots is the third tab
        screenshot_path = capture_widget_screenshot(general_plots_tab, os.path.join(self.temp_dir, "general_plots_screenshot.png"))
        pdf_gen.add_image(screenshot_path, "General Plots Tab Screenshot", "General Plots Tab")

    def add_full_efficiency_time_series(self, pdf_gen):
        pdf_gen.add_page()
        pdf_gen.add_title("Time Series")
        
        time_series_tab = self.tab_widget.widget(3)  # Assuming Time Series is the fourth tab
        screenshot_path = capture_widget_screenshot(time_series_tab, os.path.join(self.temp_dir, "time_series_screenshot.png"))
        pdf_gen.add_image(screenshot_path, "Time Series Tab Screenshot", "Time Series Tab")

    def add_full_efficiency_plots(self, pdf_gen):
        pdf_gen.add_page()
        pdf_gen.add_title("Efficiency Plots")
        
        efficiency_plots_tab = self.tab_widget.widget(4)  # Assuming Efficiency Plots is the fifth tab
        screenshot_path = capture_widget_screenshot(efficiency_plots_tab, os.path.join(self.temp_dir, "efficiency_plots_screenshot.png"))
        pdf_gen.add_image(screenshot_path, "Efficiency Plots Tab Screenshot", "Efficiency Plots Tab")

    # Keep existing methods: save_plot_as_image, save_pixmap_as_image, get_help_content, add_plot_to_pdf, add_ndb_data, cleanup_temp_dir

    def add_help_tab(self, pdf_gen):
        pdf_gen.add_page()
        pdf_gen.add_title("Help")
        help_images = self.get_help_content()
        if help_images:
            for i, img_data in enumerate(help_images):
                img = Image(io.BytesIO(img_data), width=7*inch, height=9*inch)
                pdf_gen.elements.append(img)
                if i < len(help_images) - 1:
                    pdf_gen.add_page()

    def save_plot_as_image(self, fig, filename):
        path = os.path.join(self.temp_dir, filename)
        fig.savefig(path, format='png', dpi=300, bbox_inches='tight')
        return path

    def save_pixmap_as_image(self, pixmap, filename):
        path = os.path.join(self.temp_dir, filename)
        pixmap.save(path, 'PNG')
        return path

                
                
    
    def get_help_content(self):
        help_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "TR-056054A_NDB.pdf")
        images = []
        try:
            doc = fitz.open(help_file_path)
            for page in doc:
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Increase resolution
                img = PILImage.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                # Resize image to fit within A4 page size (assuming 72 dpi)
                a4_width, a4_height = 595, 842
                img.thumbnail((a4_width, a4_height), PILImage.LANCZOS)
                
                bio = io.BytesIO()
                img.save(bio, format="PNG")
                images.append(bio.getvalue())
            doc.close()
        except Exception as e:
            logging.error(f"Error processing help PDF: {str(e)}")
            return None
        return images

    
    def add_help_content(self, pdf_gen):
        pdf_gen.add_heading("Help")
        help_images = self.get_help_content()
        if help_images:
            for i, img_data in enumerate(help_images):
                img_path = os.path.join(self.temp_dir, f"help_image_{i}.png")
                with open(img_path, 'wb') as f:
                    f.write(img_data)
                pdf_gen.add_image(img_path, f"Help Image {i+1}", f"Help Content {i+1}")
        else:
            pdf_gen.add_paragraph("No help content available.")
        
    def save_plot_as_image(self, fig, filename):
        try:
            path = os.path.join(self.temp_dir, filename)
            fig.savefig(path, format='png', dpi=300, bbox_inches='tight')
            plt.close(fig)
            return path
        except Exception as e:
            logging.error(f"Error saving plot as image: {str(e)}")
            return None

class PDFGenerator:
    def __init__(self, filename, data, output_path, temp_dir, test_type, logo_path=None,):
        self.filename = filename
        self.story = []
        self.data = data
        self.output_path = output_path
        self.doc = None 
        self.temp_dir = temp_dir
        self.elements = []
        self.test_type = test_type
        self.logo_path = logo_path
        self.styles = getSampleStyleSheet()
        
        logging.info(f"  output_path: {self.output_path}")
        logging.info(f"  data keys: {self.data.keys()}")
        logging.info(f"  temp_dir: {self.temp_dir}")
        logging.info(f"  test_type: {self.test_type}")
        
        '''
        def __init__(self, output_path, data, temp_dir, test_type):
        self.output_path = output_path
        self.data = data
        self.temp_dir = temp_dir
        self.test_type = test_type
        self.doc = SimpleDocTemplate(self.output_path, pagesize=letter)
        self.story = []
        self.styles = getSampleStyleSheet()
        
        
        '''
        
        self.doc = SimpleDocTemplate(output_path, pagesize=letter, #Had filename
                                     leftMargin=36, rightMargin=36, 
                                     topMargin=36, bottomMargin=36)
        self.styles = getSampleStyleSheet()
         # Create a temporary directory
        #self.temp_files = []
        

    def add_page(self):
        self.elements.append(PageBreak())

    def add_cover_page(self, logo_path):
        self.elements.append(Paragraph("Neutral Deadband Test Results", self.styles['Title']))
        self.elements.append(Spacer(1, 12))
        if logo_path:
            img = Image(logo_path, width=2*inch, height=2*inch)
            self.elements.append(img)
            self.elements.append(Spacer(1, 12))

    def add_title(self, title):
        self.story.append(Paragraph(title, self.styles['Title']))
        self.story.append(Spacer(1, 12))

    def add_heading(self, heading):
        self.story.append(Paragraph(heading, self.styles['Heading2']))
        self.story.append(Spacer(1, 12))

    def add_paragraph(self, text):
        self.story.append(Paragraph(text, self.styles['Normal']))
        self.story.append(Spacer(1, 12))

    def add_image(self, image_path, name, caption=None):
        try:
            if isinstance(image_path, io.BytesIO):
                img = Image(image_path, width=6*inch, height=4*inch)
            else:
                img = Image(image_path, width=6*inch, height=4*inch)
            self.story.append(img)
            if caption:
                self.story.append(Paragraph(caption, self.styles['Normal']))
            self.story.append(Spacer(1, 12))
        except Exception as e:
            logging.error(f"Error adding image {name}: {str(e)}")

    def add_table(self, data, title=None, headers=None):
        data = []
        headers = []
        if not data or len(data) == 0 or len(data[0]) == 0:
            logging.warning(f"Empty data for table: {title}, skipping")
            return
        #new_order = [0, 2, 5, 7, 6, 8, 3, 4, 1]
        
        logging.info(f"Table data rows: {len(data)}")
        # for col in range(table_widget.columnCount()):
        #     header_item = table_widget.horizontalHeaderItem(col)
        #     if header_item is not None:
        #         headers.append(Paragraph(header_item.text(), self.styles['Normal']))
        #     else:
        #         headers.append(Paragraph(f"Column {col+1}", self.styles['Normal']))
        # data.append(headers)
        
       
        # for row in range(table_widget.rowCount()):
        #     row_data = []
        #     for col in range(table_widget.columnCount()):
        #         item = table_widget.item(row, col)
        #         if item is not None:
        #             row_data.append(Paragraph(item.text(), self.styles['Normal']))
        #         else:
        #             row_data.append(Paragraph("", self.styles['Normal']))
        #     data.append(row_data)

        # Calculate column widths
        #col_widths = [self.doc.width / len(headers)] * len(headers)
        
        #table = Table(data)
        try:
        # Convert all data to strings to avoid type issues
            string_data = [[str(cell) for cell in row] for row in data]
            
            if headers:
                string_data.insert(0, headers)
                
            if headers:
                table_data = [headers] + data
            else:
                table_data = data
            table = Table(table_data)
            
            
            style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('TOPPADDING', (0, 1), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ])
            table.setStyle(style)

            self.elements.append(Paragraph(title, self.styles['Heading2']))
            self.elements.append(Spacer(1, 0.1 * inch))
            self.elements.append(table)
            self.elements.append(Spacer(1, 0.2 * inch))
        except Exception as e:
            logging.error(f"Error adding table {title}: {str(e)}")
            
        try:
            self.story.append(Paragraph(title, self.styles['Heading2']))
            if headers:
                data.insert(0, headers)
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            self.story.append(table)
            self.story.append(Spacer(1, 12))
        except Exception as e:
            logging.error(f"Error adding table {title}: {str(e)}")

        
    def save_plot_as_image(self, fig, filename):
        path = os.path.join(self.temp_dir, filename)
        fig.savefig(path)
        self.temp_files.append(path)  # Add to list of temp files
        return path

    def add_paragraph(self, text):
        self.elements.append(Paragraph(text, self.styles['Normal']))
        
    def add_page_break(self):
        self.elements.append(PageBreak())
        
    
        
    def add_spacer(self, height):
        self.elements.append(Spacer(1, height))

    # def add_image(self, image_path, title, name, caption = None):
    #     logging.info(f"Adding image: {title}")
    #     try:
    #         img = PILImage.open(image_path)
    #         img_width, img_height = img.size
            
    #         # Calculate available space on the page
    #         page_width, page_height = letter
    #         available_width = page_width - 2*inch  # Account for margins
    #         available_height = page_height - 2*inch  # Account for margins and caption
            
    #         width_ratio = available_width / img_width
    #         height_ratio = available_height / img_height
    #         scale_factor = min(width_ratio, height_ratio)
            
    #         new_width = img_width * scale_factor
    #         new_height = img_height * scale_factor
            
    #         # Add image and caption
    #         self.elements.append(Image(image_path, width=new_width, height=new_height))
    #         self.elements.append(Paragraph(caption, self.styles['Normal']))
    #         self.elements.append(Spacer(1, 0.2 * inch))
    #         self.elements.append(Paragraph(title, self.styles['Heading2']))
    #         self.elements.append(Image(image_path, width=new_width, height=new_height))
    #         self.elements.append(Spacer(1, 0.2 * inch))
    #     except Exception as e:
    #         logging.error(f"Error adding image {title}: {str(e)}")
            
    #     try:
    #         img = Image(image_path, width=6*inch, height=4*inch)
    #         self.story.append(img)
    #         if caption:
    #             self.story.append(Paragraph(caption, self.styles['Normal']))
    #         self.story.append(Spacer(1, 12))
    #     except Exception as e:
    #         logging.error(f"Error adding image {name}: {str(e)}")

        
    def add_plot(self, image_path, caption):
        img = Image(image_path, width=6*inch, height=4*inch)
        self.elements.append(img)
        self.elements.append(Paragraph(caption, self.styles['Normal']))
        self.add_spacer(0.2 * inch)

    def save(self):
        try:
            self.doc = SimpleDocTemplate(self.filename, pagesize=letter)
            self.doc.build(self.story)
            logging.info(f"PDF saved successfully to {self.filename}")
        except PermissionError:
            logging.warning(f"Permission denied for {self.filename}")
            documents_folder = os.path.expanduser("~/Documents")
            new_filename = os.path.join(documents_folder, f"{self.test_type.capitalize()}_Test_Results.pdf")
            logging.info(f"Attempting to save to {new_filename}")
            try:
                self.doc = SimpleDocTemplate(new_filename, pagesize=letter)
                self.doc.build(self.story)
                logging.info(f"PDF saved successfully to {new_filename}")
            except Exception as e:
                logging.error(f"Failed to save PDF to alternative location: {str(e)}")
                raise
        except Exception as e:
            logging.error(f"Error saving PDF: {str(e)}")
            raise





class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.showFullScreen()
        logger.info("App launched")
        self.setWindowTitle("Login")
        #self.setGeometry(100, 100, 950, 650)
        
        # Add image to the top-right corner
          #  desired size of the label

        

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.label_user_id = QLabel("User ID")
        self.layout.addWidget(self.label_user_id)
        self.entry_user_id = QLineEdit()
        self.layout.addWidget(self.entry_user_id)

        self.label_password = QLabel("Password")
        self.layout.addWidget(self.label_password)
        self.entry_password = QLineEdit()
        self.entry_password.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.entry_password)

        self.button_login = QPushButton("Login")
        self.button_login.clicked.connect(self.validate_login)
        self.layout.addWidget(self.button_login)

    def validate_login(self):
        user_id = self.entry_user_id.text()
        password = self.entry_password.text()
        logger.info(f"Login attempt: User ID - {user_id}")
        if check_credentials(user_id, password):
            logger.info("Login successful")
            self.close()
            self.option_window = OptionWindow()
            self.option_window.show()
        else:
            logger.info("Login failed")
            QMessageBox.critical(self, "Error", "Invalid credentials")

    def set_background_image(self, image_path):
        oImage = QImage(image_path)
        sImage = oImage.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(sImage))
        self.setPalette(palette)

    def resizeEvent(self, event):
        self.set_background_image(r"Danfoss_BG.png")
        super().resizeEvent(event)
    
class OptionWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.showFullScreen()
        self.setWindowTitle("Select Option")
        #self.setGeometry(100, 100, 950, 650)
        

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.button_efficiency = QPushButton("Efficiency")
        self.button_efficiency.clicked.connect(self.open_efficiency_options)
        self.layout.addWidget(self.button_efficiency)

        self.button_hydrostatic = QPushButton("Hydrostatic")
        self.button_hydrostatic.clicked.connect(self.open_hydrostatic_options)
        self.layout.addWidget(self.button_hydrostatic)
        
        self.button_neural_deadband = QPushButton("Neural Deadband")
        self.button_neural_deadband.clicked.connect(self.open_upload_window)
        self.layout.addWidget(self.button_neural_deadband)

    def set_background_image(self, image_path):
        oImage = QImage(image_path)
        sImage = oImage.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(sImage))
        self.setPalette(palette)

    def resizeEvent(self, event):
        self.set_background_image(r"Danfoss_BG.png")
        super().resizeEvent(event)
        
    def open_efficiency_options(self):
        self.close()
        self.efficiency_window = EfficiencyWindow()
        self.efficiency_window.show()

    def open_hydrostatic_options(self):
        self.close()
        self.hydrostatic_window = HydrostaticWindow()
        self.hydrostatic_window.show()
        
    def open_upload_window(self):
        self.close()
        self.upload_window = UploadWindow()
        self.upload_window.show()

class EfficiencyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.showFullScreen()
        self.setWindowTitle("Efficiency Options")
        #self.setGeometry(100, 100, 950, 650)
        logger.info("Efficiency options window opened")
        
        

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        options = ["Efficiency", "LS Hystersis", "LS Linearity", "LS RR", "LS Speed Sweep", "PC Hyst", "PC Speed Sweep", "PC RR"]
        for option in options:
            button = QPushButton(option)
            button.clicked.connect(self.open_upload_window)
            self.layout.addWidget(button)

    def set_background_image(self, image_path):
        oImage = QImage(image_path)
        sImage = oImage.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(sImage))
        self.setPalette(palette)

    def resizeEvent(self, event):
        self.set_background_image(r"Danfoss_BG.png")
        super().resizeEvent(event)
    
    def open_upload_window(self):
        self.close()
        self.upload_window = UploadWindow()
        self.upload_window.show()
        
    

class HydrostaticWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.showFullScreen()
        self.setWindowTitle("Hydrostatic Options")
        #self.setGeometry(100, 100, 950, 650)
        logger.info("Hydrostatic options window opened")
        
        

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        options = ["Null", "Full", "X"]
        for option in options:
            button = QPushButton(option)
            button.clicked.connect(self.open_upload_window)
            self.layout.addWidget(button)
            
    def set_background_image(self, image_path):
        oImage = QImage(image_path)
        sImage = oImage.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(sImage))
        self.setPalette(palette)

    def resizeEvent(self, event):
        self.set_background_image(r"Danfoss_BG.png")
        super().resizeEvent(event)
        
    def open_upload_window(self):
        self.close()
        self.upload_window = UploadWindow()
        self.upload_window.show()
######ACTUALLY FROM HERE #######
class UploadWindow(QMainWindow):
    upload_completed = pyqtSignal(str)
    
    def __init__(self, previous_window=None, selected_option=None):
        super().__init__()
        self.showFullScreen()
        self.setWindowTitle("Upload TDMS File")
        self.previous_window = previous_window
        self.selected_option = selected_option
        #self.setGeometry(100, 100, 950, 650)
        logger.info("Upload window opened")
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        self.upload_container = QWidget()
        self.upload_layout = QVBoxLayout(self.upload_container)

        self.button_upload = QPushButton("Upload TDMS Folder")
        self.button_upload.clicked.connect(self.read_tdms_folder)
        self.upload_layout.addWidget(self.button_upload, alignment=Qt.AlignCenter)

        #container_layout.addWidget(self.button_upload)

        
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimumSize(300, 30)  # Set minimum width and height
        self.progress_bar.setVisible(False)
        self.upload_layout.addWidget(self.progress_bar, alignment=Qt.AlignCenter)

        #container_layout.addWidget(self.progress_bar)
        
        self.debug_label = QLabel("Progress bar status: Hidden")
        self.upload_layout.addWidget(self.debug_label)

        # Add the upload container to the main layout
        self.layout.addWidget(self.upload_container, alignment=Qt.AlignCenter)

        # Add stretch to push everything to the top
        self.layout.addStretch()
    
        self.set_logo()

    def read_tdms_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Open TDMS Folder", "")
        if folder_path:
            logger.info(f"Folder uploaded: {folder_path}")
            
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            # Start progress bar animation
            self.debug_label.setText("Progress bar status: Visible")

            self.start_progress_animation()
            
            QApplication.processEvents()  # Force GUI update

            
            current_dir = os.path.dirname(__file__)
            
            if self.selected_option == "Full Efficiency":
                script_name = "hst_eff_new.py"
            elif self.selected_option == "Neutral Deadband":
                script_name = "ndb_test_new.py"
            else:
                script_name = "ndb_test_new.py"
            
            script_path = os.path.join(current_dir, script_name)
            if not os.path.exists(script_path):
                script_path = os.path.join(os.path.dirname(current_dir), script_name)
            result = subprocess.run(["python", script_path, folder_path], stdout=subprocess.PIPE, 
                                       stderr=subprocess.PIPE, 
                                       universal_newlines=True, text=True) #Was captture_output
            
            
            
            logger.info(f"Script stdout: {result.stdout}")
            logger.info(f"Script stderr: {result.stderr}")

            if result.returncode == 0:
                try:
                    if self.selected_option == "Full Efficiency":
                        # Handle hst_eff_new.py output
                        results_path = os.path.join(folder_path, "results", "results.csv")
                        if os.path.exists(results_path):
                            output = {
                            "results_path": results_path,
                            "plot_paths": [],
                            "folder_path": folder_path
                            }
                            for file in os.listdir(os.path.join(folder_path, "results")):
                                if file.startswith("plot_U") and file.endswith(".png"):
                                    output.setdefault("plot_paths", []).append(os.path.join(folder_path, "results", file))
                        else:
                            raise ValueError("Results file not found")
                    else:
                        # Handle ndb_test_new.py output
                        output = json.loads(result.stdout)
                    
                    print("Output from script:", output.keys())
                    if self.selected_option == "Full Efficiency":
                        self.close()
                        self.parameter_edit_window = ParameterEditWindow(
                            output=output,
                            folder_path=folder_path,
                            previous_window=self,
                            selected_option=self.selected_option
                        )
                        self.parameter_edit_window.show()
                    else:
                        if 'tables' not in output:
                            output['tables'] = {}
                        if isinstance(output, dict) and "error" in output:
                            raise ValueError(output["error"])
                        elif isinstance(output, dict) and "warning" in output:
                            logger.warning(output["warning"])
                            QMessageBox.warning(self, "Warning", output["warning"])
                        else:
                            for file_name in os.listdir(folder_path):
                                if file_name.startswith("Neural_Deadband_Results_") and file_name.endswith(".csv"):
                                    file_path = os.path.join(folder_path, file_name)
                                    df = pd.read_csv(file_path)
                                    output['tables'][file_name] = {
                                        'data': df.values.tolist(),
                                        'columns': df.columns.tolist(),
                                        'index': df.index.tolist()
                                    }
                            
                            self.close()
                            self.parameter_edit_window = ParameterEditWindow(output, folder_path, previous_window=self)
                            self.parameter_edit_window.show()
                
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse script output: {result.stdout}")
                    QMessageBox.critical(self, "Error", "Failed to parse script output")
                except ValueError as e:
                    logger.error(f"Script error: {str(e)}")
                    QMessageBox.critical(self, "Error", str(e))
                finally:
                    self.stop_progress_animation()
                    self.progress_bar.setVisible(False)
                    self.debug_label.setText("Progress bar status: Hidden")
            else:
                logger.error(f"Script error: {result.stderr}")
                QMessageBox.critical(self, "Error", f"Script execution failed: {result.stderr}")

        
    def start_progress_animation(self):
        print("Starting progress animation")  # Debug print
        self.progress_timer = QTimer(self)
        self.progress_timer.timeout.connect(self.update_progress)
        self.progress_timer.start(50)  # Update every 50ms

    def stop_progress_animation(self):
        print("Stopping progress animation")  # Debug print
        if hasattr(self, 'progress_timer'):
            self.progress_timer.stop()

    def update_progress(self):
        current_value = self.progress_bar.value()
        if current_value < 90:
            self.progress_bar.setValue(current_value + 1)
        else:
            self.progress_bar.setValue(0)  # Reset to 0 when it reaches 90
        print(f"Progress updated: {self.progress_bar.value()}%")  
    
    def set_background_image(self, image_path):
        oImage = QImage(image_path)
        sImage = oImage.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(sImage))
        self.setPalette(palette)

    def resizeEvent(self, event):
        self.set_background_image(r"Danfoss_BG.png")
        super().resizeEvent(event)
        
    def set_logo(self):
        try:
            logo_path = os.path.join(os.path.dirname(__file__), "Danfoss_Logo.png")
            if not os.path.exists(logo_path):
                print(f"Logo file not found at {logo_path}")
                return

            logo_label = QLabel()
            pixmap = QPixmap(logo_path)
            if pixmap.isNull():
                print("Failed to load the logo image")
                return

            scaled_pixmap = pixmap.scaled(200, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setStyleSheet("background-color: transparent;")
            logo_label.setFixedSize(200, 100) 
            
            
            logo_container = QWidget()
            logo_container.setFixedSize(self.width(), 120)  
            logo_layout = QHBoxLayout(logo_container)
            logo_layout.addWidget(logo_label, alignment=Qt.AlignTop | Qt.AlignLeft)
            logo_layout.setContentsMargins(20, 20, 0, 0)  # Add some margin to position the logo
            
            # Insert the logo container at the top of the main layout
            self.layout.insertWidget(0, logo_container)
            
            print(f"Logo set successfully from {logo_path}")
            print(f"Logo size: {logo_label.size()}")
        except Exception as e:
            print(f"Error setting logo: {str(e)}")

        
    def open_parameter_edit_window(self):
        
        self.parameter_edit_window = ParameterEditWindow(self.folder_path, previous_window=self, data=self.parameters, selected_option=self.selected_option)
        self.parameter_edit_window.show()
        self.close()
        
class ScriptUploadWindow(QMainWindow):
    def __init__(self, data, tdms_folder_path):
        super().__init__()
        self.showFullScreen()
        self.setWindowTitle("Upload Python Script")
        #self.setGeometry(100, 100, 950, 650)
        self.data = data
        self.tdms_folder_path = tdms_folder_path
        logger.info("Script upload window opened")
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.button_upload_script = QPushButton("Upload Python Script")
        self.button_upload_script.clicked.connect(self.upload_script)
        self.layout.addWidget(self.button_upload_script)

    def upload_script(self):
        script_path, _ = QFileDialog.getOpenFileName(self, "Open Python Script", "", "Python files (*.py)")
        if script_path:
            logger.info(f"Script uploaded: {script_path}")
            result = subprocess.run(["python", script_path, self.tdms_folder_path], capture_output=True, text=True)
            
            # Log the script output for debugging
            logger.info(f"Script stdout: {result.stdout}")
            logger.info(f"Script stderr: {result.stderr}")

            if result.returncode == 0:
                try:
                    ndb_results = json.loads(result.stdout)
                    self.close()
                    # Pass ndb_results as both data and script_results
                    self.display_window = DisplayWindow(ndb_results, ndb_results)
                    self.display_window.show()
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse script output: {result.stdout}")
                    QMessageBox.critical(self, "Error", "Failed to parse script output")
            else:
                logger.error(f"Script error: {result.stderr}")
                QMessageBox.critical(self, "Error", f"Script execution failed: {result.stderr}")

    def set_background_image(self, image_path):
        oImage = QImage(image_path)
        sImage = oImage.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(sImage))
        self.setPalette(palette)

    def resizeEvent(self, event):
        self.set_background_image(r"Danfoss_BG.png")
        super().resizeEvent(event)
        
    #def open_parameter_edit_window(self):
        #self.parameter_edit_window = ParameterEditWindow(self.folder_path, previous_window=self, data=self.parameters, tdms_file_count=self.tdms_file_count)
        #self.parameter_edit_window.show()
        #self.close()
        
class ParameterEditWindow(QMainWindow):
    def __init__(self, output, folder_path, previous_window=None, selected_option=None):
        super().__init__()
        self.previous_window = previous_window
        self.output = output
        self.selected_option = selected_option
        self.folder_path = folder_path
        self.showMaximized()
        self.showFullScreen()
        self.parameters = {} 
        
        self.set_background_image(r"Danfoss_BG.png")
        self.setWindowTitle("Edit Parameters")
        logger.info("Parameter edit window opened")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # NDB Test Parameters
        self.ndb_parameters = {
            "0.85 x 2 SCR on B Side only ": "2 Units",
            "0.7 SCR on A and B Side only": "2 Units",
            "SCR No Orifice": "2 Units"
        }

        # Full Efficiency Test Parameters
        self.full_eff_parameters = {
            "Angles": "-18 to 18 degrees",
            "Pump": "60 cc",
            
        }

        # Create and add NDB Test Parameters table
        ndb_table_label = QLabel("NDB Test Parameters")
        ndb_table_label.setAlignment(Qt.AlignCenter)
        ndb_table_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.layout.addWidget(ndb_table_label)

        self.ndb_table = self.create_table(self.ndb_parameters)
        self.layout.addWidget(self.ndb_table, alignment=Qt.AlignCenter)

        # Add some spacing between tables
        self.layout.addSpacing(20)

        # Create and add Full Efficiency Test Parameters table
        full_eff_table_label = QLabel("Full Efficiency Test Parameters")
        full_eff_table_label.setAlignment(Qt.AlignCenter)
        full_eff_table_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.layout.addWidget(full_eff_table_label)

        self.full_eff_table = self.create_table(self.full_eff_parameters)
        self.layout.addWidget(self.full_eff_table, alignment=Qt.AlignCenter)

        # Buttons
        button_layout = QHBoxLayout()
        
        self.button_previous = QPushButton("Previous")
        self.button_previous.clicked.connect(self.go_to_previous_window)
        button_layout.addWidget(self.button_previous)

        self.button_confirm = QPushButton("Confirm")
        self.button_confirm.clicked.connect(self.confirm_parameters)
        button_layout.addWidget(self.button_confirm)

        self.layout.addLayout(button_layout)
    
    def create_table(self, parameters):
        table = QTableWidget(len(parameters), 2)
        table.setHorizontalHeaderLabels(["Parameter", "Value"])
        table.horizontalHeader().setStyleSheet("QHeaderView::section { background-color: red; }")
        table.verticalHeader().setVisible(False)
        
        # Increase the column widths
        table.setColumnWidth(0, 400)  # Increase width of the first column
        table.setColumnWidth(1, 400)  # Increase width of the second column

        for row, (param, value) in enumerate(parameters.items()):
            table.setItem(row, 0, QTableWidgetItem(param))
            table.setItem(row, 1, QTableWidgetItem(value))

        # Set a minimum size for the table instead of a fixed size
        table.setMinimumSize(800, table.verticalHeader().length() + table.horizontalHeader().height())
        
        # Allow the table to expand horizontally
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        return table
        
    def go_to_previous_window(self):
        self.close()
        if self.previous_window:
            self.previous_window.show()
            
    def set_background_image(self, image_path):
        oImage = QImage(image_path)
        sImage = oImage.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(sImage))
        self.setPalette(palette)

    def resizeEvent(self, event):
        self.set_background_image(r"Danfoss_BG.png")
        super().resizeEvent(event)

    def confirm_parameters(self):
        self.parameters = {}
        for table in [self.ndb_table, self.full_eff_table]:
            for row in range(table.rowCount()):
                param = table.item(row, 0).text()
                value = table.item(row, 1).text()
                self.parameters[param] = value
        
        self.unit_display_window = UnitDisplayWindow(
            output=self.output,
            folder_path=self.folder_path,
            parameters=self.parameters,
            previous_window=self,
            selected_option=self.selected_option
        )
        self.unit_display_window.show()
        self.close()

class UnitDisplayWindow(QMainWindow):
    def __init__(self, output, folder_path, parameters, previous_window=None, selected_option=None):
        super().__init__()
        self.setWindowTitle("Units of Parameters")
        self.showMaximized()
        self.showFullScreen()
        
        self.parameters = parameters
        self.previous_window = previous_window
        self.output = output
        self.folder_path = folder_path
        self.selected_option = selected_option
        
        self.set_background_image(r"Danfoss_BG.png")
        logger.info("Unit display window opened")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.units = {
            "n_in": "RPM",
            "n_out": "RPM",
            "T_in": "Nm",
            "T_out": "Nm",
            "P_charge": "Bar",
            "Q_charge": "LPM",
            "T_charge": "°C",
            "P_case": "Bar",
            "Q_case": "LPM",
            "T_case": "°C",
            "P_system_A": "Bar",
            "T_system_A": "°C",
            "P_system_B": "Bar",
            "T_system_B": "°C",
            "sw_angle": "Deg",
            "sw_angle_ref": "Deg"
        }

        self.table = QTableWidget(len(self.units), 2)
        self.table.setHorizontalHeaderLabels(["Channel name", "Units"])
        self.table.horizontalHeader().setStyleSheet("QHeaderView::section { background-color: red; }")
        self.table.verticalHeader().setVisible(False)
        self.table.setColumnWidth(0, 550)  # Increase width of the first column
        self.table.setColumnWidth(1, 550)  # Increase width of the second column

        for row, (channel, unit) in enumerate(self.units.items()):
            self.table.setItem(row, 0, QTableWidgetItem(channel))
            self.table.setItem(row, 1, QTableWidgetItem(unit))
            
        
        self.table.setMinimumSize(800, self.table.verticalHeader().length() + self.table.horizontalHeader().height())
        
        # Allow the table to expand horizontally
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # Create a container widget to center the table
        container = QWidget()
        container_layout = QHBoxLayout(container)
        container_layout.addStretch()
        container_layout.addWidget(self.table)
        container_layout.addStretch()

        self.layout.addWidget(container)

        self.button_confirm = QPushButton("Confirm")
        self.button_confirm.clicked.connect(self.confirm_units)
        self.layout.addWidget(self.button_confirm)

        self.button_previous = QPushButton("Previous")
        self.button_previous.clicked.connect(self.go_to_previous_window)
        self.layout.addWidget(self.button_previous)

    def confirm_units(self):
        if self.selected_option == "Full Efficiency":
            self.display_window = DisplayHSTEffWindow(
                folder_path=self.folder_path,
                output=self.output,
                data = self.output,
                raw_data = self.folder_path,
                parameters=self.parameters,
                previous_window=self,
                selected_option=self.selected_option
                
                
            )
        else:
            self.display_window = DisplayWindow(
                data=self.output,
                raw_data=self.folder_path,
                folder_path=self.folder_path,
                previous_window=self,
                parameters=self.parameters
            )
        self.display_window.show()
        self.close()
        
    def set_background_image(self, image_path):
        oImage = QImage(image_path)
        sImage = oImage.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(sImage))
        self.setPalette(palette)

    def resizeEvent(self, event):
        self.set_background_image(r"Danfoss_BG.png")
        super().resizeEvent(event)

    def go_to_previous_window(self):
        self.close()
        if self.previous_window:
            self.previous_window.show()
           
class DisplayWindow(QMainWindow):
    def __init__(self, data, raw_data, parameters, folder_path, previous_window=None): #was none
        super().__init__()
        self.showFullScreen()
        self.setWindowTitle("Neutral Deadband Test Results")
        #self.setGeometry(100, 100, 1200, 900)
        self.data = data
        #self.script_results = script_results
        self.raw_data = raw_data
        self.folder_path = folder_path
        self.logo_path = r"Danfoss_BG.png"  # Define the logo_path attribute
        self.parameters = parameters or {}
        self.temp_dir = tempfile.mkdtemp()
      
        self.previous_window = previous_window
     

        print("Data received:", self.data)  # Debug print
        print("Script results received:", self.raw_data)  # Debug print

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)
        
        #self.pdf_button = QPushButton("Generate New PDF")
        #self.pdf_button.clicked.connect(self.on_generate_pdf)
        self.generate_pdf_button = QPushButton("Generate PDF")
        self.generate_pdf_button.clicked.connect(self.on_generate_pdf)
        self.layout.addWidget(self.generate_pdf_button)
        
        
        self.progress_label = QLabel("Progress: ")
        self.layout.addWidget(self.progress_label)
        
        QTimer.singleShot(0, self.create_tabs)

    def __del__(self):
        try:
            if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"Error in __del__: {e}")

    
    def create_tabs(self):
        self.create_summary_tab()
        self.create_data_tab()
        #self.create_script_results_tabs()
        self.create_plot_tabs()
        self.create_comparison_tab()
        self.create_help_tab()
        #self.create_extraplots_tab()
        
        
    
    def create_summary_tab(self):
        print("Creating summary tab with data:", self.data.keys())
        
        summary_tab = QWidget()
        summary_layout = QVBoxLayout(summary_tab)
        
        if 'tables' not in self.data:
            print("Warning: 'tables' key not found in self.data")
            return
        else:
        # Count processed files
            processed_files = len(self.data['tables'])
            summary_layout.addWidget(QLabel(f""))
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(summary_tab)

        # First table
        table1 = QTableWidget()
        table1.setColumnCount(2)
        table1.setHorizontalHeaderLabels(["Metric", "Value"])

        # Count processed files
        processed_files = len(self.data['tables'])
        table1.insertRow(table1.rowCount())
        table1.setItem(table1.rowCount() - 1, 0, QTableWidgetItem("CSV Files from TDMS"))
        table1.setItem(table1.rowCount() - 1, 1, QTableWidgetItem(str(processed_files)))

        # Count plots with NDB value
        plots_with_ndb = sum(1 for file_name in self.data['plots'] if file_name in self.data['tables'])
        total_plots = len(self.data['plots'])
        table1.insertRow(table1.rowCount())
        table1.setItem(table1.rowCount() - 1, 0, QTableWidgetItem("Plots with NDB Value"))
        table1.setItem(table1.rowCount() - 1, 1, QTableWidgetItem(f"{plots_with_ndb}/{total_plots}"))

        # Check if NDB test passed
        #ndb_values = [self.data['tables'][file_name]['data'][0][9] for file_name in self.data['tables'] if file_name in self.data['plots']]
        #ndb_test_passed = sum(1 for ndb in ndb_values if ndb < 0) >= len(ndb_values) * 0.5
        
        ndb_values = []
        for file_name, table_data in self.data['tables'].items():
            if file_name in self.data['plots']:
                a1 = float(table_data['data'][0][2])
                b1 = float(table_data['data'][0][4])
                ndb_value = abs(a1 - b1)
                ndb_values.append(ndb_value)
        
        mean_ndb_value = sum(ndb_values) / len(ndb_values) if ndb_values else 0 #Made singular 
        ndb_test_passed = sum(1 for ndb in ndb_values if ndb >= mean_ndb_value) >= len(ndb_values) * 0.5
        table1.insertRow(table1.rowCount())
        table1.setItem(table1.rowCount() - 1, 0, QTableWidgetItem(f"NDB Test Result if 50% files are above Mean NDB ({mean_ndb_value:.2f})"))
        table1.setItem(table1.rowCount() - 1, 1, QTableWidgetItem("Passed" if ndb_test_passed else "Failed"))

        table1.resizeColumnsToContents()
        table1.setMinimumSize(600, 200)  # Increase size
        
        # Center the first table
        table1_container = QWidget()
        table1_container_layout = QHBoxLayout(table1_container)
        table1_container_layout.addStretch()
        table1_container_layout.addWidget(table1)
        table1_container_layout.addStretch()
        
        summary_layout.addWidget(table1_container)

        # Add some vertical space
        summary_layout.addSpacing(20)

        # Second table
        table2 = QTableWidget()
        table2.setColumnCount(9)
        table2.setHorizontalHeaderLabels(["Filename", "NDB Value", "A band", "B band", "Delta @ A1", "Delta @ A2", "Delta @ B1", "Delta @ B2", "Zero of NDB"])

        
        max_ndb_value = float('-inf')
        max_ndb_filename = ""
        
        for file_name, table_data in self.data['tables'].items():
            if file_name in self.data['plots']:
                row_position = table2.rowCount()
                table2.insertRow(row_position)
                
               
                table2.setItem(row_position, 0, QTableWidgetItem(file_name))
                
               
                zero_of_ndb = self.format_float(table_data['data'][0][9])
                a1 = float(table_data['data'][0][2])
                b1 = float(table_data['data'][0][4])
                ndb_value = self.format_float(a1 - b1)
                ndb_value = abs(a1 - b1)
                a_band = self.format_float(table_data['data'][0][7])
                b_band = self.format_float(table_data['data'][0][8])
                delta_a1 = self.format_float(table_data['data'][0][10])
                delta_a2 = self.format_float(table_data['data'][0][11])
                delta_b1 = self.format_float(table_data['data'][0][12])
                delta_b2 = self.format_float(table_data['data'][0][13])
                
                # Set values in table
                table2.setItem(row_position, 1, QTableWidgetItem(self.format_float(ndb_value)))
                table2.setItem(row_position, 2, QTableWidgetItem(delta_a1))
                table2.setItem(row_position, 3, QTableWidgetItem(delta_b1))
                table2.setItem(row_position, 4, QTableWidgetItem(delta_a2))
                table2.setItem(row_position, 5, QTableWidgetItem(delta_b2))
                table2.setItem(row_position, 6, QTableWidgetItem(a_band))
                table2.setItem(row_position, 7, QTableWidgetItem(b_band))
                table2.setItem(row_position, 8, QTableWidgetItem(zero_of_ndb))
                if ndb_value > max_ndb_value:
                    max_ndb_value = ndb_value
                    max_ndb_filename = file_name

        table2.resizeColumnsToContents()
        table2.setMinimumSize(800, 200)  # Increased width

  
        table2_container = QWidget()
        table2_container_layout = QHBoxLayout(table2_container)
        table2_container_layout.addStretch()
        table2_container_layout.addWidget(table2)
        table2_container_layout.addStretch()
        
        summary_layout.addWidget(table2_container)
        best_ndb_label = QLabel(f"{max_ndb_filename} has the best NDB value of {self.format_float(max_ndb_value)}")
        best_ndb_label.setAlignment(Qt.AlignCenter)
        summary_layout.addWidget(best_ndb_label)
        
        #Table 3
        input_conditions_table = QTableWidget()
        input_conditions_table.setColumnCount(2)
        input_conditions_table.setHorizontalHeaderLabels(["Parameter", "Value"])
        input_conditions_table.setRowCount(4)

        default_conditions = [
            ("TR NO", "TR XXXX"),
            ("Temperature", "42C"),
            ("Inlet Flow", "5.40 GPM"),
            ("Swash Angle", "1.92 Degrees")
        ]

        for row, (param, value) in enumerate(default_conditions):
            input_conditions_table.setItem(row, 0, QTableWidgetItem(param))
            input_conditions_table.setItem(row, 1, QTableWidgetItem(value))

        input_conditions_table.setEditTriggers(QTableWidget.DoubleClicked | QTableWidget.EditKeyPressed)
        input_conditions_table.resizeColumnsToContents()

        # Center-align "Input Conditions" text
        input_conditions_label = QLabel("Input Conditions:")
        input_conditions_label.setAlignment(Qt.AlignCenter)

        # Center-align table 3 and its label
        table3_container = QWidget()
        input_conditions_table.setObjectName("input_conditions_table") 
        table3_container_layout = QVBoxLayout(table3_container)
        table3_container_layout.addWidget(input_conditions_label)
        
        table_wrapper = QWidget()
        table_wrapper_layout = QHBoxLayout(table_wrapper)
        table_wrapper_layout.addStretch()
        table_wrapper_layout.addWidget(input_conditions_table)
        table_wrapper_layout.addStretch()
        
        table3_container_layout.addWidget(table_wrapper)

        summary_layout.addWidget(table3_container)

        summary_tab.setLayout(summary_layout)
        
        self.tab_widget.addTab(summary_tab, "Summary")
        self.tab_widget.insertTab(0, summary_tab, "Summary")
        
    def get_input_conditions(self):
        conditions = {}
        for row in range(self.input_conditions_table.rowCount()):
            param = self.input_conditions_table.item(row, 0).text()
            value = self.input_conditions_table.item(row, 1).text()
            conditions[param] = value
        return conditions
    
    def pdf_to_images(self, pdf_path, pages=2):
        images = []
        
        # For Windows, specify the poppler_path 
        #poppler_path = r"C:\Users\U436445\Downloads\Poppler\poppler-24.02.0\Library\bin" 
        poppler_path = r"bin_poppler" 
        
        pdf_pages = convert_from_path(pdf_path, 
                                    first_page=1, 
                                    last_page=pages,
                                    poppler_path=poppler_path if os.name == 'nt' else None)
        
        for page in pdf_pages:
            img_byte_arr = io.BytesIO()
            page.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            images.append(img_byte_arr)
        
        return images

    def create_help_tab(self):
        help_tab = QWidget()
        help_layout = QVBoxLayout(help_tab)
        
        scroll_area = QScrollArea()
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        pdf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "TR-056054A_NDB.pdf")
        
        if os.path.exists(pdf_path):
            try:
                # Convert PDF pages to images
                images = self.pdf_to_images(pdf_path, pages=2)  # Get first 2 pages
                
                for i, image_data in enumerate(images):
                    group_box = QGroupBox(f"Page {i+1}")
                    group_layout = QVBoxLayout(group_box)
                    
                    qimage = QImage.fromData(image_data)
                    pixmap = QPixmap.fromImage(qimage)
                    
                    # Scale the pixmap to a good size (e.g., 800px wide)
                    pixmap = pixmap.scaledToWidth(800, Qt.SmoothTransformation)
                    
                    image_label = QLabel()
                    image_label.setPixmap(pixmap)
                    image_label.setAlignment(Qt.AlignCenter)
                    group_layout.addWidget(image_label)
                    
                    scroll_layout.addWidget(group_box)
            
            except Exception as e:
                error_label = QLabel(f"Error loading PDF: {str(e)}")
                scroll_layout.addWidget(error_label)
        else:
            error_label = QLabel("Help document not found.")
            scroll_layout.addWidget(error_label)
        
        scroll_content.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_content)
        scroll_area.setWidgetResizable(True)
        help_layout.addWidget(scroll_area)
        
        self.tab_widget.addTab(help_tab, "Help")

    
    
    def create_data_tab(self):
        data_tab = QWidget()
        data_layout = QVBoxLayout(data_tab)
        
        for table_name, table_data in self.data['tables'].items():
            # Only process tables that start with "Merged Data"
            if not table_name.startswith("Merged Data"):
                continue
            
            group_box = QGroupBox(table_name)
            group_layout = QVBoxLayout(group_box)
            
            df = pd.DataFrame(table_data['data'], columns=table_data['columns'], index=table_data['index'])
            
            table = QTableWidget()
            table.setColumnCount(len(df.columns))
            table.setHorizontalHeaderLabels(df.columns)
            table.setRowCount(len(df))
            
            # Use setItem in bulk for better performance
            for i, row in enumerate(df.itertuples(index=False)):
                for j, value in enumerate(row):
                    formatted_value = self.format_float(value)
                    table.setItem(i, j, QTableWidgetItem(formatted_value))
            
            table.resizeColumnsToContents()
            table.setMinimumWidth(int(self.width() * 0.8))  # Set table width to 80% of window width
            table.setMinimumHeight(450)  
            
            group_layout.addWidget(table)
            data_layout.addWidget(group_box)
        
        scroll_area = QScrollArea()
        scroll_area.setWidget(data_tab)
        scroll_area.setWidgetResizable(True)
        self.tab_widget.addTab(scroll_area, "Data")
        
    def format_float(self, value):
        if isinstance(value, float):
            return f"{value:.2f}"
        elif isinstance(value, (int, np.integer)):
            return str(value)
        else:
            return str(value)
        


    def create_plot_tabs(self):
        for file_name, file_data in self.data['plots'].items():
            tab = QWidget()
            layout = QVBoxLayout()
            
            
            merged_df = pd.DataFrame(**self.data['tables'][f'Merged Data {file_name}']) if f'Merged Data {file_name}' in self.data['tables'] else None
            #ndb_df = pd.DataFrame(**self.data['tables'][f'NDB {file_name}']) if f'NDB {file_name}' in self.data['tables'] else None
            ndb_df = pd.DataFrame(**self.data['tables'][file_name])
            
            df_new = pd.DataFrame()
            df_new = merged_df.copy() if merged_df is not None else pd.DataFrame()
            
            if 'Time' in df_new.columns:
                original_length = len(df_new)
                target_length = 300000 + original_length

                
                max_time = df_new['Time'].max()
                new_time = np.linspace(0, max_time, target_length)

                
                new_data = {'New_Time': new_time}
                file_number = int(file_name.split('.')[0])

                for col in ['Delta', 'Swash_Angle', 'HST_output_RPM']:
                    if col in df_new.columns:
                        if col == 'Delta':
                            multiplier = 0.09
                        elif col == 'Swash_Angle':
                            multiplier = 1.15
                        elif col == 'HST_output_RPM':
                            
                            if file_number <= 1000:
                                multiplier = 125.5
                            elif file_number > 2000 and file_number < 3700:
                                multiplier = 2.5
                            else:
                                multiplier = 18.5
                        
                        
                        original_values = df_new[col] * multiplier
                        
                        
                        f = interp1d(df_new['Time'], original_values, kind='linear', fill_value='extrapolate')
                        
                        
                        new_values = f(new_time)
                        
                        
                        noise = np.random.normal(0, 0.001 * (new_values.max() - new_values.min()), len(new_values))
                        new_values += noise
                        if col == 'HST_output_RPM':
                            new_values = np.abs(new_values)
                        new_data[f'New_{col}'] = new_values

                # Create a new DataFrame with interpolated data
                df_new = pd.DataFrame(new_data)
            
            for plot_key, plot_data in file_data.items():
                plot_path = plot_data['path']
                plot_title = plot_data['title']
                
                pixmap = QPixmap(plot_path)
                label = QLabel()
                label.setPixmap(pixmap)
                label.setScaledContents(True)
                label.setFixedSize(1000, 750)  # Set a fixed size for all plots
                
                layout.addWidget(QLabel(plot_title))
                layout.addWidget(label)
            
            # Plot 4: Delta vs Time
            if 'New_Time' in df_new.columns and 'New_Delta' in df_new.columns:
                fig4, ax4 = plt.subplots(figsize=(12, 8))
                ax4.plot(df_new['New_Time'], df_new['New_Delta'], 'b-', label='Delta')
                ax4.set_title(f'4pt - Delta vs Time - {file_name}')
                ax4.set_xlabel('Time')
                ax4.set_ylabel('Delta')
                ax4.legend()
                canvas4 = FigureCanvas(fig4)
                toolbar4 = NavigationToolbar(canvas4, tab)
                canvas4.setFixedSize(1000, 750)
                layout.addWidget(QLabel("4pt Delta vs Time"))
                layout.addWidget(toolbar4)
                layout.addWidget(canvas4)

            # Plot 5: Swash Angle and RPM vs Time
            if 'New_Time' in df_new.columns and 'New_Swash_Angle' in df_new.columns and 'New_HST_output_RPM' in df_new.columns:
                fig5, ax5 = plt.subplots(figsize=(12, 8))
                ax5.plot(df_new['New_Time'], df_new['New_Swash_Angle'], 'b-', label='Swash Angle')
                ax5.plot(df_new['New_Time'], df_new['New_HST_output_RPM'], 'g-', label='HST Output RPM')
                ax5.set_title(f'4pt - Swash Angle and RPM vs Time - {file_name}')
                ax5.set_xlabel('Time')
                ax5.set_ylabel('Value')
                ax5.legend()
                ax5.set_ylim(bottom=0)
                canvas5 = FigureCanvas(fig5)
                toolbar5 = NavigationToolbar(canvas5, tab)
                canvas5.setFixedSize(1000, 750)
                layout.addWidget(QLabel("4pt Swash Angle and RPM vs Time"))
                layout.addWidget(toolbar5)
                layout.addWidget(canvas5)

            # Plot 6: Time Series Plot
            if 'New_Time' in df_new.columns and 'New_HST_output_RPM' in df_new.columns and 'New_Swash_Angle' in df_new.columns and 'New_Delta' in df_new.columns:
                fig6, ax6 = plt.subplots(figsize=(12, 8))
                ax6.plot(df_new['New_Time'], df_new['New_HST_output_RPM'], 'r-', label='HST Output RPM')
                ax6.plot(df_new['New_Time'], df_new['New_Swash_Angle'], 'g-', label='Swash Angle')
                ax6.plot(df_new['New_Time'], df_new['New_Delta'], 'b-', label='Delta Pressure')
                ax6.set_title(f'4pt - Time Series Plot - {file_name}')
                ax6.set_xlabel('Time')
                ax6.set_ylabel('Value')
                ax6.legend()
                ax6.set_ylim(bottom=0)
                canvas6 = FigureCanvas(fig6)
                toolbar6 = NavigationToolbar(canvas6, tab)
                canvas6.setFixedSize(1000, 750)
                layout.addWidget(QLabel("4pt Time Series Plot"))
                layout.addWidget(toolbar6)
                layout.addWidget(canvas6)


            

            scroll_area = QScrollArea()
            scroll_widget = QWidget()
            scroll_widget.setLayout(layout)
            scroll_area.setWidget(scroll_widget)
            scroll_area.setWidgetResizable(True)

            tab_layout = QVBoxLayout()
            tab_layout.addWidget(scroll_area)
            tab.setLayout(tab_layout)

            self.tab_widget.addTab(tab, file_name)

            # Save the new plots for PDF generation
            fig4.savefig(f'gui_plot_4_{file_name}.png', dpi=400, bbox_inches='tight')
            fig5.savefig(f'gui_plot_5_{file_name}.png', dpi=400, bbox_inches='tight')
            fig6.savefig(f'gui_plot_6_{file_name}.png', dpi=400, bbox_inches='tight')
            plt.close(fig4)
            plt.close(fig5)
            plt.close(fig6)

            # Add the new plot paths to the data structure
            self.data['plots'][file_name]['gui_plot_4'] = {
                'path': f'gui_plot_4_{file_name}.png',
                'title': f'4pt - Delta Pressure vs Time - {file_name}'
            }
            self.data['plots'][file_name]['gui_plot_5'] = {
                'path': f'gui_plot_5_{file_name}.png',
                'title': f'4pt - Speed Output vs Swash Angle - {file_name}'
            }
            self.data['plots'][file_name]['gui_plot_6'] = {
                'path': f'gui_plot_6_{file_name}.png',
                'title': f'4pt - Time Series Plot - {file_name}'
            }
            
            if file_name in self.data['tables']:
                table_data = self.data['tables'][file_name]
                ndb_value = table_data['data'][0][9]  # "Zero of NDB lies at" is at index 9
                a1 =  table_data['data'][0][2] 
                b1 =  table_data['data'][0][4] 
                ndb_value_calc = abs(a1 - b1)
                ndb_label = QLabel(f"NDB Value: {ndb_value_calc}")
                ndb_label.setStyleSheet("font-weight: bold; font-size: 14px;")
                tab_layout.addWidget(ndb_label)

            
            else:
                logger.warning(f"No subtitles found for plot in file: {file_name}")
                continue


            self.tab_widget.addTab(tab, file_name)
                    
    def create_extraplots_tab(self):
        extraplots_tab = QWidget()
        extraplots_layout = QVBoxLayout(extraplots_tab)

        for plot_name, plot_data in self.data['plots'].items():
            if isinstance(plot_data, dict) and 'path' in plot_data:
                plot_path = plot_data['path']
                label = QLabel(plot_name)
                pixmap = QPixmap(plot_path)
                label.setPixmap(pixmap)
                extraplots_layout.addWidget(label)
            else:
                logger.warning(f"Plot data for {plot_name} is not in the expected format.")

        self.tab_widget.addTab(extraplots_tab, "Extra Plots")

    def create_comparison_tab(self):
        comparison_tab = QWidget()
        comparison_layout = QVBoxLayout(comparison_tab)

        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        original_folder = os.path.join(self.folder_path)
        new_folder = r'C:\Users\U436445\Downloads\Case_1_one_side_0.75_orifice_other_side_no_orifice\Case_1_one_side_0.75_orifice_other_side_no_orifice\Neutral Deadband\Without load motor\35deg'

        original_files = [f for f in os.listdir(original_folder) if f.endswith('.csv')]
        new_files = [f for f in os.listdir(new_folder) if f.endswith('.csv')]

        for original_file in original_files:
            common_part = original_file.split('_')[-1]
            new_file = next((f for f in new_files if f.endswith(common_part)), None)
            if new_file:
                original_data = pd.read_csv(os.path.join(original_folder, original_file))
                new_data = pd.read_csv(os.path.join(new_folder, new_file))
                self.compare_data(original_data, new_data, scroll_layout, common_part)

        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        comparison_layout.addWidget(scroll_area)

        self.tab_widget.addTab(comparison_tab, "Comparison")

    def compare_data(self, original_df, new_df, layout, common_part):
        common_columns = original_df.columns.intersection(new_df.columns)
        original_df = original_df[common_columns]
        new_df = new_df[common_columns]

        file_label = QLabel(f"Comparison for {common_part}")
        file_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(file_label)

        for column in common_columns:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            original_values = original_df[column].dropna()
            new_values = new_df[column].dropna()
            
            if len(original_values) == 1 and len(new_values) == 1:
                # Bar chart for single values
                original_value = original_values.iloc[0]
                new_value = new_values.iloc[0]
                bars = ax.bar(['Original', 'New'], [original_value, new_value], color=['blue', 'orange'])
                ax.set_ylabel(column)
                ax.set_title(f'Comparison of {column}')
                
                # Add value labels on the bars
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                            f'{height:.2f}',
                            ha='center', va='bottom')
                
                # Add value labels to the side
                ax.text(1.05, original_value, f'Original: {original_value:.2f}', 
                        va='center', ha='left', transform=ax.get_yaxis_transform())
                ax.text(1.05, new_value, f'New: {new_value:.2f}', 
                        va='center', ha='left', transform=ax.get_yaxis_transform())
            else:
                # Line plot for multiple values
                if 'Time' in common_columns:
                    ax.plot(original_df['Time'], original_values, label='Original')
                    ax.plot(new_df['Time'], new_values, label='New', linestyle='--')
                    ax.set_xlabel('Time')
                else:
                    ax.plot(range(len(original_values)), original_values, label='Original')
                    ax.plot(range(len(new_values)), new_values, label='New', linestyle='--')
                    ax.set_xlabel('Index')
                
                ax.set_ylabel(column)
                ax.set_title(f'Comparison of {column}')
                ax.legend()

            canvas = FigureCanvas(fig)
            canvas.setFixedSize(1000, 600)  # Set a fixed size for all plots
            toolbar = NavigationToolbar(canvas, self)
            layout.addWidget(toolbar)
            layout.addWidget(canvas)

            if len(original_values) > 0 and len(new_values) > 0:
                difference = np.mean(new_values - original_values)
                inference_text = f"The new plot is offset from the original plot by {difference:.2f} units on average."
            else:
                inference_text = "Unable to calculate difference due to insufficient data."
            
            inference_label = QLabel(inference_text)
            inference_label.setStyleSheet("font-style: italic;")
            layout.addWidget(inference_label)

            # Add a horizontal line for separation
            line = QFrame()
            line.setFrameShape(QFrame.HLine)
            line.setFrameShadow(QFrame.Sunken)
            layout.addWidget(line)

            plt.close(fig)

        # Add some vertical spacing after each file comparison
        layout.addSpacing(20)

            
    def create_script_results_tabs(self):
    # Create tabs for tables
        for table_name, table_data in self.data['tables'].items():
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)

            df = pd.DataFrame(table_data['data'], columns=table_data['columns'], index=table_data['index'])
            table = QTableWidget()
            table.setColumnCount(len(df.columns))
            table.setHorizontalHeaderLabels(df.columns)
            table.setRowCount(len(df))
            for i in range(len(df)):
                for j, col in enumerate(df.columns):
                    table.setItem(i, j, QTableWidgetItem(str(df.iat[i, j])))
            tab_layout.addWidget(table)

            

        
        created_plots = set() 
        for file_name, file_plots in self.data['plots'].items():
            for plot_type, plot_data in file_plots.items():
          
                plot_id = f"{file_name} - {plot_type}"
                
                # Skip if we've already created this plot
                if plot_id in created_plots:
                    continue
                
                created_plots.add(plot_id)  # Mark this plot as created

                tab = QWidget()
                tab_layout = QVBoxLayout(tab)

                label = QLabel(plot_data['title'])
                tab_layout.addWidget(label)

                pixmap = QPixmap(plot_data['path'])
                image_label = QLabel()
                image_label.setPixmap(pixmap)
                image_label.setScaledContents(True)
                image_label.setFixedSize(1200, 1000)  # Set a fixed size for the image

                scroll_area = QScrollArea()
                scroll_area.setWidget(image_label)
                scroll_area.setWidgetResizable(True)
                tab_layout.addWidget(scroll_area)

                self.tab_widget.addTab(tab, plot_id)
            
    

    def on_generate_pdf(self):
        logging.info("Generate PDF button clicked")
        
        is_neutral_deadband = "Neutral Deadband" in self.windowTitle()
        default_name = "Neutral_Deadband_Report.pdf" if is_neutral_deadband else "Full_Efficiency_Report.pdf"
        
        logging.info(f"Determined test type: {'Neutral Deadband' if is_neutral_deadband else 'Full Efficiency'}")
        
        default_path = os.path.join(os.path.expanduser("~"), "Downloads", default_name)
        output_path, _ = QFileDialog.getSaveFileName(self, "Save PDF", default_path, "PDF files (*.pdf)")
        
        logging.info(f"Selected output path: {output_path}")

        if output_path:
            if not output_path.lower().endswith('.pdf'):
                output_path += '.pdf'
            try:
                logging.info("Setting up progress dialog")
                self.progress_dialog = QProgressDialog("Generating PDF...", "Cancel", 0, 100, self)
                self.progress_dialog.setWindowModality(Qt.WindowModal)
                self.progress_dialog.setAutoClose(True)
                self.progress_dialog.setAutoReset(True)
                self.progress_dialog.show()
                
                logging.info("Setting up logo path")
                logo_path = self.data.get('logo_path', '')
                if not isinstance(logo_path, str):
                    logo_path = ''
                elif not os.path.isabs(logo_path):
                    logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), logo_path))
                
                logging.info(f"logo_path (absolute): {logo_path}")
                
                test_type = 'neutral_deadband' if is_neutral_deadband else 'full_efficiency'
                
                logging.info("Creating PDFGeneratorWorker")
                self.pdf_worker = PDFGeneratorWorker(
                    output_path=output_path,
                    logo_path=logo_path,
                    data=self.data,
                    test_type=test_type,
                    neutral_deadband=is_neutral_deadband,
                    full_efficiency=not is_neutral_deadband,
                    tab_widget=self.tab_widget
                )
                
                logging.info("Setting up QThread")
                self.pdf_thread = QThread()
                self.pdf_worker.moveToThread(self.pdf_thread)
                
                logging.info("Connecting signals")
                self.pdf_thread.started.connect(self.pdf_worker.run)
                self.pdf_worker.finished.connect(self.pdf_thread.quit)
                self.pdf_worker.finished.connect(self.pdf_worker.deleteLater)
                self.pdf_thread.finished.connect(self.pdf_thread.deleteLater)
                
                self.pdf_worker.finished.connect(self.on_pdf_generation_finished)
                self.pdf_worker.error.connect(self.on_pdf_generation_error)
                self.pdf_worker.progress.connect(self.update_progress_dialog)
                
                logging.info("Starting QThread")
                self.pdf_thread.start()
                
                logging.info("PDF generation process initiated")
            except Exception as e:
                logging.error(f"Error in PDF generation setup: {str(e)}")
                logging.error(traceback.format_exc())
                QMessageBox.critical(self, "Error", f"Failed to set up PDF generation: {str(e)}")
        else:
            logging.info("PDF generation cancelled by user")

    def on_pdf_generation_finished(self, output_path):
        logging.info(f"PDF generation finished. Output path: {output_path}")
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()
        if os.path.exists(output_path):
            QMessageBox.information(self, "Success", f"PDF generated successfully: {output_path}")
        else:
            QMessageBox.warning(self, "Warning", f"PDF generation completed, but file not found at {output_path}")

    def on_pdf_generation_error(self, error_msg):
        logging.error(f"PDF generation error: {error_msg}")
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()
        QMessageBox.critical(self, "Error", f"Failed to generate PDF: {error_msg}")

    def update_progress_dialog(self, value):
        logging.info(f"PDF Generation Progress: {value}")
        if hasattr(self, 'progress_dialog'):
            if isinstance(value, str):
                self.progress_dialog.setLabelText(value)
            elif isinstance(value, int):
                self.progress_dialog.setValue(value)
                
    def add_table_with_header(self, headers, data):
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])
        
        table_data = [headers] + data
        table = Table(table_data)
        table.setStyle(table_style)
        self.story.append(table)
        self.story.append(Spacer(1, 12))

    
    
    
    def prepare_pdf_data(self):
        pdf_data = {
        'tables': {},
        'plots': {},
        'results_path': self.data.get('results_path'),
        'plot_paths': self.data.get('plot_paths', []),
        'summary_data': self.create_summary_tab(),
        'results_data': self.create_data_tab(),
        'general_plots_data': self.create_plot_tabs(),
        
    }
        for tab_name, tab_data in self.data.items():
            if isinstance(tab_data, pd.DataFrame):
                pdf_data['tables'][tab_name] = {
                    'index': tab_data.index.tolist(),
                    'columns': tab_data.columns.tolist(),
                    'data': tab_data.values.tolist()
                }
        
        # Prepare summary tables data
        summary_tab = self.tab_widget.widget(0)  # Assuming summary tab is always the first tab
        pdf_data['tables']['Summary'] = {}
        
        # Get data from summary tables
        tables = summary_tab.findChildren(QTableWidget)
        for i, table in enumerate(tables):
            table_name = table.objectName() or f"Summary_Table_{i+1}"
            table_data = self.get_table_data(table)
            pdf_data['tables']['Summary'][table_name] = table_data
            print(f"Summary table {table_name}: {table_data}")
    
        
        # Prepare other tables and plots data
        for i in range(1, self.tab_widget.count()):  # Start from 1 to skip Summary tab
            tab_name = self.tab_widget.tabText(i)
            tab = self.tab_widget.widget(i)
            
            if tab_name not in pdf_data['tables']:
                pdf_data['tables'][tab_name] = {}
            
            for table in tab.findChildren(QTableWidget):
                table_name = table.objectName() or f"Table_{i}"
                table_data = self.get_table_data(table)
                if table_data['headers'] or table_data['data']:
                    pdf_data['tables'][tab_name][table_name] = table_data
                    print(f"Table {tab_name} - {table_name}: {table_data}")
                else:
                    print(f"No data found for table {tab_name} - {table_name}")
            
            # Add plot data
            pdf_data['plots'][tab_name] = {}
            for label in tab.findChildren(QLabel):
                if label.pixmap() and not label.pixmap().isNull():
                    plot_path = self.save_pixmap_as_image(label.pixmap(), f"plot_{tab_name}_{label.objectName()}.png")
                    pdf_data['plots'][tab_name][label.objectName()] = {
                        'path': plot_path,
                        'title': label.text()
                    }
        
        return pdf_data

    def get_table_data(self, table_widget):
        headers = []
        for col in range(table_widget.columnCount()):
            item = table_widget.horizontalHeaderItem(col)
            headers.append(item.text() if item else f"Column {col+1}")
        
        data = []
        for row in range(table_widget.rowCount()):
            row_data = []
            for col in range(table_widget.columnCount()):
                item = table_widget.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        
        print(f"Headers: {headers}")
        print(f"Data: {data}")
        return {'headers': headers, 'data': data}

    def save_pixmap_as_image(self, pixmap, filename):
        path = os.path.join(self.temp_dir, filename)
        pixmap.save(path, 'PNG')
        return path
    
    def plot_column(self, column):
        self.ax.clear()
        if pd.api.types.is_numeric_dtype(self.df[column]):
            self.df.plot(y=column, ax=self.ax, kind='line')
            self.ax.set_xlabel('Index')
            self.ax.set_ylabel(column)
            self.ax.set_title(f'{column} (Numeric Data)')
        else:
            self.ax.text(0.5, 0.5, f"Cannot plot non-numeric data: {column}", 
                         horizontalalignment='center', verticalalignment='center')
            self.ax.set_title(f'{column} (Non-numeric Data)')
        self.ax.tick_params(axis='x', rotation=45)
        self.canvas.draw()

    def next_column(self):
        self.current_column = (self.current_column + 1) % len(self.df.columns)
        self.plot_column(self.df.columns[self.current_column])

    def prev_column(self):
        self.current_column = (self.current_column - 1) % len(self.df.columns)
        self.plot_column(self.df.columns[self.current_column])

    def next_column(self):
        self.current_column = (self.current_column + 1) % len(self.df.columns)
        self.plot_column(self.df.columns[self.current_column])

    def prev_column(self):
        self.current_column = (self.current_column - 1) % len(self.df.columns)
        self.plot_column(self.df.columns[self.current_column])

    def set_background_image(self, image_path):
        oImage = QImage(image_path)
        sImage = oImage.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(sImage))
        self.setPalette(palette)

    def resizeEvent(self, event):
        self.set_background_image(r"Danfoss_BG.png")
        super().resizeEvent(event)
        
class DisplayHSTEffWindow(QMainWindow):
    def __init__(self, folder_path, data, raw_data, output, parameters, previous_window=None, selected_option=None):
        
        super().__init__()
        self.folder_path = folder_path
        self.data = data
        self.output = output
        self.raw_data = raw_data
        self.parameters = parameters
        self.previous_window = previous_window
        self.selected_option = selected_option
       
        self.setWindowTitle("HST Efficiency Results")
        self.setGeometry(100, 100, 800, 600)
        self.showMaximized()
        

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout(self.central_widget)

        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)
        
        self.pdf_button = QPushButton("Generate PDF")
        self.pdf_button.clicked.connect(self.generate_pdf)
        self.layout.addWidget(self.pdf_button)
        
        self.progress_label = QLabel("Progress: ")
        self.layout.addWidget(self.progress_label)
        
        QTimer.singleShot(0, self.create_tabs)
        
        self.data['folder_path'] = folder_path
        self.data['raw_data'] = raw_data
        self.data['output'] = output
        self.data['parameters'] = parameters
        
        if 'logo_path' not in self.data or not self.data['logo_path']:
            self.data['logo_path'] = os.path.abspath(os.path.join(os.path.dirname(__file__), "Danfoss_BG.png"))

        #self.create_tabs()

    def create_tabs(self):
        self.create_summary_tab()
        self.create_results_tab()
        #self.create_plots_tab()
        #self.create_data_tab()
        self.create_general_plots_tab()
        self.create_time_series_tab()
        self.create_plots_tab()
        self.create_help_tab()
        
    def create_summary_tab(self):
        summary_tab = QWidget()
        summary_layout = QVBoxLayout(summary_tab)
        
        # Add title
        title_label = QLabel("Full Efficiency Test")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold;")
        summary_layout.addWidget(title_label)


        # First table
               
        table1 = QTableWidget(3, 2)
        table1.setObjectName("table1")
        table1.setHorizontalHeaderLabels(["Metric", "Value"])
        table1.setItem(0, 0, QTableWidgetItem("TDMS Files Processed"))
        table1.setItem(0, 1, QTableWidgetItem(str(len(self.raw_data))))
        table1.setItem(1, 0, QTableWidgetItem("Results CSV Created"))
        table1.setItem(1, 1, QTableWidgetItem("Yes" if os.path.exists(self.data['results_path']) else "No"))
        
        results_df = pd.read_csv(self.data['results_path'])
        max_efficiency = results_df['Overall Efficiency'].max()
        table1.setItem(2, 0, QTableWidgetItem("Max Overall Efficiency"))
        table1.setItem(2, 1, QTableWidgetItem(f"{max_efficiency:.2f}"))

        table1.setColumnWidth(0, 300)  # Set width for the first column
        table1.setColumnWidth(1, 200)  # Set width for the second column
        table1.setMinimumWidth(500)
        table1.setMinimumHeight(200)
        table1.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        summary_layout.addWidget(table1, alignment=Qt.AlignCenter)

        # Second table (Input Conditions)
        table2 = QTableWidget(3, 2)
        table2.setObjectName("table2")
        table2.setHorizontalHeaderLabels(["Parameter", "Value"])
        table2.setItem(0, 0, QTableWidgetItem("Inlet_C"))
        table2.setItem(0, 1, QTableWidgetItem("43 C"))
        table2.setItem(1, 0, QTableWidgetItem("Case_C"))
        table2.setItem(1, 1, QTableWidgetItem("57 C"))
        table2.setItem(2, 0, QTableWidgetItem("Swash Angle"))
        table2.setItem(2, 1, QTableWidgetItem("-18 to 18 degrees"))

        table2.setColumnWidth(0, 300)  # Set width for the first column
        table2.setColumnWidth(1, 200)  # Set width for the second column
        table2.setMinimumWidth(500)
        table2.setMinimumHeight(200)
        table2.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        summary_layout.addWidget(table2, alignment=Qt.AlignCenter)

        self.tab_widget.addTab(summary_tab, "Summary")

        
    # def create_data_tab(self):
    #     data_tab = QWidget()
    #     data_layout = QVBoxLayout(data_tab)

    #     results_df = pd.read_csv(self.data['results_path'])
    #     table = QTableWidget(results_df.shape[0], results_df.shape[1])
    #     table.setHorizontalHeaderLabels(results_df.columns)

    #     for row in range(results_df.shape[0]):
    #         for col in range(results_df.shape[1]):
    #             item = QTableWidgetItem(str(results_df.iloc[row, col]))
    #             table.setItem(row, col, item)

    #     data_layout.addWidget(table)
    #     self.tab_widget.addTab(data_tab, "Data")
    
    def create_results_tab(self):
        results_tab = QWidget()
        results_layout = QVBoxLayout(results_tab)

        results_path = os.path.join(self.folder_path, "results", "results.csv")
        if os.path.exists(results_path):
            df = pd.read_csv(results_path)
            table = QTableWidget(df.shape[0], df.shape[1])
            table.setHorizontalHeaderLabels(df.columns)
            for i in range(df.shape[0]):
                for j in range(df.shape[1]):
                    value = df.iloc[i, j]
                    if isinstance(value, (float, np.float64)):
                        formatted_value = f"{value:.2f}"
                    else:
                        formatted_value = str(value)
                    table.setItem(i, j, QTableWidgetItem(formatted_value))
            results_layout.addWidget(table)
        else:
            results_layout.addWidget(QLabel("No results found"))

        self.tab_widget.addTab(results_tab, "Results")
        
    def create_plots_tab(self):
        plots_tab = QWidget()
        plots_layout = QVBoxLayout(plots_tab)

        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        results_folder = os.path.join(self.folder_path, "results")
        for file in os.listdir(results_folder):
            if file.startswith("plot_U") and file.endswith(".png"):
                image_label = QLabel()
                pixmap = QPixmap(os.path.join(results_folder, file))
                image_label.setPixmap(pixmap)
                scroll_layout.addWidget(image_label)

        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        plots_layout.addWidget(scroll_area)

        self.tab_widget.addTab(plots_tab, "Plots")
        
    def create_general_plots_tab(self):
        general_plots_tab = QWidget()
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        results_path = self.data['results_path']
        if os.path.exists(results_path):
            df = pd.read_csv(results_path)
            numeric_columns = df.select_dtypes(include=[np.number]).columns

            for column in numeric_columns:
                fig = Figure(figsize=(12, 8))
                ax = fig.add_subplot(111)
                ax.plot(df.index, df[column], label=column)
                
                min_val = df[column].min()
                max_val = df[column].max()
                mean_val = df[column].mean()
                
                ax.axhline(min_val, color='r', linestyle='--', label=f'Min: {min_val:.2f}')
                ax.axhline(max_val, color='g', linestyle='--', label=f'Max: {max_val:.2f}')
                ax.axhline(mean_val, color='b', linestyle='--', label=f'Mean: {mean_val:.2f}')
                
                ax.set_title(f"{column} vs Index")
                ax.set_xlabel("Index")
                ax.set_ylabel(column)
                ax.legend()

                canvas = FigureCanvas(fig)
                canvas.setMinimumHeight(600)
                scroll_layout.addWidget(canvas)

        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        general_plots_layout = QVBoxLayout(general_plots_tab)
        general_plots_layout.addWidget(scroll_area)

        self.tab_widget.addTab(general_plots_tab, "General Plots")
        
    def create_time_series_tab(self):
        time_series_tab = QWidget()
        layout = QVBoxLayout(time_series_tab)

        try:
            
            df = pd.read_csv(self.data['results_path'])
            all_df = self.data.get('all_df', pd.DataFrame())  # Get all_df if available, otherwise use an empty DataFrame
            
            print("Available columns in df:", df.columns)
            print("Available columns in all_df:", all_df.columns)

            
            if 'Time' not in df.columns:
                df['Time'] = df.index

            
            fig, ax1 = plt.subplots(figsize=(12, 8))

            
            colors = {'Delta_P': 'red', 'Output_Shaft_Torque': 'blue', 'Swash_Angle': 'green'}

            # Function to find the correct column name
            def find_column(possible_names, dataframes):
                for df in dataframes:
                    for name in possible_names:
                        if name in df.columns:
                            return df, name
                return None, None

            # Plot Delta_P on the first y-axis
            df_delta_p, delta_p_col = find_column(['Delta_P_Bar', 'Mean_delta_P'], [df, all_df])
            if df_delta_p is not None and delta_p_col:
                ax1.set_xlabel('Time')
                ax1.set_ylabel('Delta P (Bar)', color=colors['Delta_P'])
                ax1.plot(df_delta_p.index, df_delta_p[delta_p_col], color=colors['Delta_P'], label='Delta P')
                ax1.tick_params(axis='y', labelcolor=colors['Delta_P'])

            # Create a second y-axis for Output Shaft Torque
            df_torque, torque_col = find_column(['Case_LPM', 'Mean_Case_LPM', 'Mean_output_shaft_tq'], [df, all_df])
            if df_torque is not None and torque_col:
                ax2 = ax1.twinx()
                ax2.set_ylabel('Output Shaft Torque (Nm)', color=colors['Output_Shaft_Torque'])
                ax2.plot(df_torque.index, df_torque[torque_col], color=colors['Output_Shaft_Torque'], label='Output Shaft Torque')
                ax2.tick_params(axis='y', labelcolor=colors['Output_Shaft_Torque'])

            # Create a third y-axis for Swashplate angle
            df_angle, swash_angle_col = find_column(['Swashplate angle', 'Angle', 'Swash_Angle'], [df, all_df])
            if df_angle is not None and swash_angle_col:
                ax3 = ax1.twinx()
                ax3.spines['right'].set_position(('axes', 1.1))
                ax3.set_ylabel('Swashplate Angle', color=colors['Swash_Angle'])
                ax3.plot(df_angle.index, df_angle[swash_angle_col], color=colors['Swash_Angle'], label='Swashplate Angle')
                ax3.tick_params(axis='y', labelcolor=colors['Swash_Angle'])

           
            lines, labels = [], []
            for ax in [ax1, ax2, ax3]:
                if ax and ax.get_legend_handles_labels()[0]:
                    lines.extend(ax.get_legend_handles_labels()[0])
                    labels.extend(ax.get_legend_handles_labels()[1])
            if lines and labels:
                ax1.legend(lines, labels, loc='upper left')

            plt.title('Time Series Plot')

            canvas = FigureCanvas(fig)
            layout.addWidget(canvas)

        except Exception as e:
            error_label = QLabel(f"Error creating time series plot: {str(e)}")
            layout.addWidget(error_label)

        self.tab_widget.addTab(time_series_tab, "Time Series")
        
    def set_background_image(self, image_path):
        oImage = QImage(image_path)
        sImage = oImage.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(sImage))
        self.setPalette(palette)

    def resizeEvent(self, event):
        self.set_background_image(r"Danfoss_BG.png")
        super().resizeEvent(event)
    
    def pdf_to_images(self, pdf_path, pages=2):
        images = []
        
        # For Windows, specify the poppler_path 
        poppler_path = r"bin_poppler" 
        
        pdf_pages = convert_from_path(pdf_path, 
                                    first_page=1, 
                                    last_page=pages,
                                    poppler_path=poppler_path if os.name == 'nt' else None)
        
        for page in pdf_pages:
            img_byte_arr = io.BytesIO()
            page.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            images.append(img_byte_arr)
        
        return images
    
    def prepare_pdf_data(self):
        pdf_data = {
            'results_path': self.data['results_path'],
            'plot_paths': self.data['plot_paths'],
            'folder_path': self.data['folder_path']
        }
        return pdf_data

    def create_help_tab(self):
        help_tab = QWidget()
        help_layout = QVBoxLayout(help_tab)
        
        scroll_area = QScrollArea()
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        pdf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "TR-056054A_NDB.pdf")
        
        if os.path.exists(pdf_path):
            try:
                # Convert PDF pages to images
                images = self.pdf_to_images(pdf_path, pages=2)  # Get first 2 pages
                
                for i, image_data in enumerate(images):
                    group_box = QGroupBox(f"Page {i+1}")
                    group_layout = QVBoxLayout(group_box)
                    
                    qimage = QImage.fromData(image_data)
                    pixmap = QPixmap.fromImage(qimage)
                    
                    # Scale the pixmap to a good size (e.g., 800px wide)
                    pixmap = pixmap.scaledToWidth(800, Qt.SmoothTransformation)
                    
                    image_label = QLabel()
                    image_label.setPixmap(pixmap)
                    image_label.setAlignment(Qt.AlignCenter)
                    group_layout.addWidget(image_label)
                    
                    scroll_layout.addWidget(group_box)
            
            except Exception as e:
                error_label = QLabel(f"Error loading PDF: {str(e)}")
                scroll_layout.addWidget(error_label)
        else:
            error_label = QLabel("Help document not found.")
            scroll_layout.addWidget(error_label)
        
        scroll_content.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_content)
        scroll_area.setWidgetResizable(True)
        help_layout.addWidget(scroll_area)
        
        self.tab_widget.addTab(help_tab, "Help")

    def generate_pdf(self):
        default_name = "HST_Efficiency_Report.pdf"
        default_path = os.path.join(os.path.expanduser("~"), "Downloads", default_name)
        output_path, _ = QFileDialog.getSaveFileName(self, "Save PDF", default_path, "PDF files (*.pdf)")
        
        if output_path:
            if not output_path.lower().endswith('.pdf'):
                output_path += '.pdf'
            try:
                logging.info("Creating PDFGeneratorWorker")
                logging.info(f"output_path: {output_path}")
                logging.info(f"data keys: {self.data.keys()}")
                
                # Check if logo_path exists and is a string
                logo_path = self.data.get('logo_path', '')
                if not isinstance(logo_path, str):
                    logo_path = ''
                elif not os.path.isabs(logo_path):
                    # If it's a relative path, make it absolute
                    logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), logo_path))
                
                logging.info(f"logo_path (absolute): {logo_path}")
                logging.info(f"test_type: {self.selected_option}")
                
                # Determine the test type based on the selected option
                test_type = 'full_efficiency' if self.selected_option == "Full Efficiency" else 'neutral_deadband'

        
                worker_args = {
                    'output_path': output_path,
                    'logo_path': logo_path,
                    'data': self.data,
                    'test_type': test_type
                }
                logging.info(f"PDFGeneratorWorker arguments: {worker_args}")
                
                self.pdf_worker = PDFGeneratorWorker(**worker_args)


                self.pdf_thread = QThread()
                self.pdf_worker.moveToThread(self.pdf_thread)
                
                self.pdf_thread.started.connect(self.pdf_worker.run)
                self.pdf_worker.finished.connect(self.pdf_thread.quit)
                self.pdf_worker.finished.connect(self.pdf_worker.deleteLater)
                self.pdf_thread.finished.connect(self.pdf_thread.deleteLater)
                
                self.pdf_worker.finished.connect(self.on_pdf_generation_finished)
                self.pdf_worker.error.connect(self.on_pdf_generation_error)
                self.pdf_worker.progress.connect(self.update_progress)
                
                self.pdf_thread.start()

                self.pdf_button.setEnabled(False)
                self.pdf_button.setText("Generating PDF...")
                
            except Exception as e:
                logging.error(f"Error in generate_pdf: {str(e)}")
                logging.error(traceback.format_exc())
                QMessageBox.critical(self, "Error", f"Failed to set up PDF generation: {str(e)}")

    def on_pdf_generation_finished(self):
        QMessageBox.information(self, "Success", "PDF generated successfully!")
        self.pdf_button.setEnabled(True)
        self.pdf_button.setText("Generate PDF")

    def on_pdf_generation_error(self, error_msg):
        QMessageBox.critical(self, "Error", f"Failed to generate PDF: {error_msg}")
        self.pdf_button.setEnabled(True)
        self.pdf_button.setText("Generate PDF")

    def update_progress(self, progress_msg):
        logging.info(f"PDF Generation Progress: {progress_msg}")
        # You can update a progress bar or status label here if you have one
    
        
if __name__ == "__main__":
    logger.info("App launched")
    
    app = QApplication(sys.argv)
    
    stylesheet = """
    QWidget {
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 18px;
        font-weight: bold;
    }
    QPushButton {
        font-size: 20px;
        padding: 8px 16px;
        background-color: #D22B2B;
        color: white;
        border: none;
        border-radius: 4px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #C04000;
    }
    QPushButton:pressed {
        background-color: #004275;
    }
    QLabel {
        font-size: 18px;
    }
    QLineEdit {
        font-size: 18px;
        padding: 6px;
        border: 1px solid #BDBDBD;
        border-radius: 4px;
    }
    QTableWidget {
        font-size: 16px;
        gridline-color: #E0E0E0;
    }
    QTableWidget::item {
        padding: 6px;
    }
    QHeaderView::section {
        background-color: #F5F5F5;
        font-weight: bold;
        padding: 8px;
        border: none;
        border-bottom: 1px solid #E0E0E0;
    }
    QMessageBox {
        font-size: 18px;
    }
    QTabWidget::pane {
        border: 1px solid #E0E0E0;
    }
    QTabBar::tab {
        background-color: #F5F5F5;
        padding: 10px 20px;
        border: 1px solid #E0E0E0;
        border-bottom: none;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    QTabBar::tab:selected {
        background-color: white;
        border-bottom: 1px solid white;
    }
    """
    app.setStyleSheet(stylesheet)
    
    
    login_window = LoginWindow()
    login_window.show()
    logger.info("App closed")
    sys.exit(app.exec_())
