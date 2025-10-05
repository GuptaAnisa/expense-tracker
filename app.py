from flask import Flask, render_template, request, redirect, url_for, flash
import os
import shutil
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
from password_vault import FILE_CATEGORIES, get_category, organize_files

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'


def generate_visualization(directory_path):
    """Generate visualization of file organization"""
    # Get file counts by category
    file_counts = {category: 0 for category in FILE_CATEGORIES.keys()}

    for root, _, files in os.walk(directory_path):
        for file in files:
            category = get_category(file)
            if category in file_counts:
                file_counts[category] += 1

    # Create plot
    plt.figure(figsize=(10, 6))
    sns.barplot(x=list(file_counts.keys()), y=list(file_counts.values()))
    plt.title('File Organization Summary')
    plt.xlabel('File Categories')
    plt.ylabel('Number of Files')
    plt.xticks(rotation=45)

    # Save plot to bytes
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_data = base64.b64encode(img.getvalue()).decode('utf-8')
    plt.close()

    return plot_data


@app.route('/', methods=['GET', 'POST'])
def index():
    context = {
        'FILE_CATEGORIES': FILE_CATEGORIES
    }

    if request.method == 'POST':
        directory_path = request.form['directory_path']

        if not os.path.exists(directory_path):
            flash('Error: Directory does not exist! ❌', 'error')
            return redirect(url_for('index'))

        try:
            organize_files(directory_path)
            context['plot_data'] = generate_visualization(directory_path)
            context['directory_path'] = directory_path
            flash('All files organized successfully! 🎉', 'success')
        except Exception as e:
            flash(f'Error organizing files: {str(e)}', 'error')

        return render_template('index.html', **context)

    return render_template('index.html', **context)


if __name__ == '__main__':
    app.run(debug=True)
