from flask import Flask, render_template, request, send_file, redirect, url_for, flash
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime  # This is the critical import
# from fpdf import FPDF
from fpdf import FPDF, XPos, YPos  # Updated for new FPDF2 syntax
from io import BytesIO
import base64
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Initialize DataFrame with persistence
DATA_FILE = 'expenses.csv'


def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["Date", "Category", "Amount", "Description"])


def save_data(df):
    df.to_csv(DATA_FILE, index=False)


@app.route("/", methods=["GET", "POST"])
def index():
    df = load_data()
    plot = None
    categories = ["Food", "Transport", "Entertainment",
                  "Housing", "Utilities", "Other"]

    if request.method == "POST":
        try:
            # Add new expense
            if 'add_expense' in request.form:
                new_expense = pd.DataFrame([{
                    "Date": request.form['date'],
                    "Category": request.form['category'],
                    "Amount": float(request.form['amount']),
                    "Description": request.form['description']
                }])

                df = pd.concat([df, new_expense], ignore_index=True)
                save_data(df)
                flash('Expense added successfully!', 'success')

            # Delete expense
            elif 'delete' in request.form:
                index = int(request.form['delete'])
                df = df.drop(index).reset_index(drop=True)
                save_data(df)
                flash('Expense deleted successfully!', 'success')

            return redirect(url_for('index'))

        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')

    # Generate plot if requested
    if 'generate_plot' in request.args and not df.empty:
        plot = generate_plot(df)

    return render_template("index.html",
                           expenses=df.to_dict('records'),
                           plot=plot,
                           categories=categories,
                           total=df['Amount'].sum() if not df.empty else 0,
                           datetime=datetime)


# ------------------------------------------------------------------------------------------

def generate_plot(df):
    plt.switch_backend('Agg')  # Needed for thread safety
    category_totals = df.groupby("Category")["Amount"].sum()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

    # Pie chart
    ax1.pie(category_totals, labels=category_totals.index,
            autopct="%1.1f%%", startangle=90)
    ax1.set_title("Expenses by Category (%)")

    # Bar chart
    category_totals.sort_values().plot(kind='barh', ax=ax2)
    ax2.set_title("Expenses by Category ($)")
    ax2.set_xlabel("Amount")

    plt.tight_layout()

    img = BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode('utf8')


@app.route("/export/<file_type>")
def export(file_type):
    df = load_data()
    if df.empty:
        flash('No data to export!', 'warning')
        return redirect(url_for('index'))

    try:
        if file_type == 'excel':
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            output.seek(0)
            return send_file(
                output,
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                as_attachment=True,
                download_name=f"expenses_{datetime.now().strftime('%Y%m%d')}.xlsx"
            )
    

        elif file_type == 'pdf':
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            #Title
            pdf.cell(200, 10, txt="Expense Report", ln=1, align="C")
            pdf.ln(10)
            
            # Table header
            pdf.set_fill_color(200, 220, 255)
            pdf.cell(40, 10, "Date", 1, 0, 'C', 1)
            pdf.cell(40, 10, "Category", 1, 0, 'C', 1)
            pdf.cell(30, 10, "Amount", 1, 0, 'C', 1)
            pdf.cell(80, 10, "Description", 1, 1, 'C', 1)

            # Table rows
            pdf.set_fill_color(255, 255, 255)
            for _, row in df.iterrows():
                pdf.cell(40, 10, str(row['Date']), 1)
                pdf.cell(40, 10, str(row['Category']), 1)
                pdf.cell(30, 10, f"${row['Amount']:.2f}", 1)
                pdf.cell(80, 10, str(row['Description']), 1)
                pdf.ln()

             # Summary
            pdf.ln(10) 
            pdf.cell(0, 10, f"Total Expenses: ${df['Amount'].sum():.2f}", 0, 1, 'R')

            pdf_output = pdf.output() 
            return send_file(
                BytesIO(pdf_output),
                mimetype="application/pdf",
                as_attachment=True,
                download_name=f"expenses_{datetime.now().strftime('%Y%m%d')}.pdf"
    )
    
    except Exception as e:
        flash(f'Export failed: {str(e)}', 'danger')
        return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
