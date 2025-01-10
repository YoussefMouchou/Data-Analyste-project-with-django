import base64
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import dash_core_components as dcc
from django.shortcuts import render, redirect
from django.http import HttpResponse
import plotly.express as px
import plotly.graph_objects as go
# Global dataframe variable to store the uploaded data
dataframe = None

def home(request):
    return render(request, 'home.html')

def upload_file(request):
    global dataframe  # Use a global variable (if necessary, but not ideal for production)

    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']

        # Check if the uploaded file is a CSV
        if not csv_file.name.endswith('.csv'):
            return render(request, 'upload.html', {'error': "Veuillez télécharger un fichier CSV valide."})

        try:
            # Try reading the uploaded CSV into a pandas dataframe
            dataframe = pd.read_csv(csv_file)

            # Redirect to the "View Data" page after successful upload
            return redirect('view_data')
        except Exception as e:
            # Handle CSV parsing errors
            return render(request, 'upload.html', {'error': f"Erreur lors du traitement du fichier : {str(e)}"})

    # Render the upload page for GET requests or if no file is uploaded
    return render(request, 'upload.html')

def view_data(request):
    global dataframe
    if dataframe is not None:
        table_html = dataframe.head().to_html()
        return render(request, 'view_data.html', {'data_table': table_html})
def index_data(request):
    global dataframe
    context = {}
    
    # Vérifier si le dataframe existe et ajouter les colonnes au contexte immédiatement
    if dataframe is not None:
        # Convertir les colonnes en liste et les ajouter au contexte
        context['columns'] = list(dataframe.columns)
        context['total_rows'] = len(dataframe)
        
        if request.method == 'POST':
            index = request.POST.get('index')
            column_name = request.POST.get('column_name')
            
            if index:
                try:
                    index = int(index)
                    if 0 <= index < len(dataframe):
                        context['row_data'] = dataframe.iloc[index].to_dict()
                    else:
                        context['error'] = "Index hors limites."
                except ValueError:
                    context['error'] = "Index invalide."
            
            if column_name:
                if column_name in dataframe.columns:
                    context['column_data'] = dataframe[column_name].tolist()
                else:
                    context['error'] = "Colonne non trouvée."
    else:
        context['error'] = "Aucun dataset n'a été chargé."

    return render(request, 'index_data.html', context)

def analyze_data(request):
    global dataframe

    # Check if the dataframe exists and is not empty
    if dataframe is None or dataframe.empty:
        return HttpResponse("Aucune donnée n'est disponible pour l'analyse. Veuillez télécharger un fichier CSV valide.")

    # Store original missing values count before replacement
    original_missing = {
        'total_missing': dataframe.isnull().sum().sum(),
        'missing_by_column': dataframe.isnull().sum().to_dict()
    }

    # Create a copy of the dataframe to avoid modifying the original
    df_clean = dataframe.copy()

    # Dictionary to store replacement methods used
    replacement_info = {}

    # Handle missing values for each column
    for column in df_clean.columns:
        missing_count = df_clean[column].isnull().sum()
        
        if missing_count > 0:
            if pd.api.types.is_numeric_dtype(df_clean[column]):
                # Pour les colonnes numériques
                if df_clean[column].isnull().sum() / len(df_clean) > 0.5:
                    # Si plus de 50% de valeurs manquantes, utiliser la moyenne
                    replacement_value = df_clean[column].mean()
                    replacement_method = "moyenne"
                else:
                    # Sinon utiliser la médiane
                    replacement_value = df_clean[column].median()
                    replacement_method = "médiane"
                
                df_clean[column].fillna(replacement_value, inplace=True)
                
            else:
                # Pour les colonnes catégorielles
                if df_clean[column].isnull().sum() / len(df_clean) > 0.5:
                    # Si plus de 50% de valeurs manquantes, utiliser "Inconnu"
                    df_clean[column].fillna("Inconnu", inplace=True)
                    replacement_method = "valeur 'Inconnu'"
                else:
                    # Sinon utiliser le mode
                    replacement_value = df_clean[column].mode()[0]
                    df_clean[column].fillna(replacement_value, inplace=True)
                    replacement_method = "mode"

            replacement_info[column] = {
                'missing_count': int(missing_count),
                'missing_percentage': round((missing_count / len(df_clean)) * 100, 2),
                'replacement_method': replacement_method
            }

    if request.method == 'POST':
        column_name = request.POST.get('column_name')
        response = {}

        if column_name and column_name in df_clean.columns:
            column = df_clean[column_name]
            response['statistics'] = {
                'mean': column.mean() if pd.api.types.is_numeric_dtype(column) else None,
                'median': column.median() if pd.api.types.is_numeric_dtype(column) else None,
                'std': column.std() if pd.api.types.is_numeric_dtype(column) else None,
                'min': column.min() if pd.api.types.is_numeric_dtype(column) else None,
                'max': column.max() if pd.api.types.is_numeric_dtype(column) else None
            }

        # Add missing values information
        response['missing_values'] = {
            'original': original_missing,
            'replacement_info': replacement_info,
            'remaining_missing': {
                'total_missing': df_clean.isnull().sum().sum(),
                'missing_by_column': df_clean.isnull().sum().to_dict()
            }
        }

        # Add columns list
        response['columns'] = df_clean.columns.tolist()

        # Add df.describe() and df.info() outputs for cleaned data
        response['describe'] = df_clean.describe(include='all').to_html(
            classes='table table-striped',
            float_format=lambda x: f'{x:.2f}' if isinstance(x, float) else x
        )

        # Get DataFrame info
        buffer = io.StringIO()
        df_clean.info(buf=buffer)
        response['info'] = buffer.getvalue()

        # Update global dataframe with cleaned version
        dataframe = df_clean

        return render(request, 'analyze.html', response)

    # For GET requests, show the form to enter a column name
    return render(request, 'analyze.html', {
        'columns': df_clean.columns.tolist(),
        'missing_values': {
            'original': original_missing,
            'replacement_info': replacement_info
        }
    })
def visualize_data(request):
    """
    Handle the visualization of data based on user input from an HTTP request.
    This view function processes GET and POST requests to render a web page for data visualization.
    It supports various plot types including histograms, box plots, scatter plots, bar charts, and correlation matrices.
    Args:
        request (HttpRequest): The HTTP request object containing metadata about the request.
    Returns:
        HttpResponse: An HTTP response object with the rendered HTML content.
    Raises:
        ValueError: If the required columns for a specific plot type are not provided or if an unsupported plot type is requested.
    Context:
        columns (list): List of all column names in the dataframe.
        numeric_columns (list): List of numeric column names in the dataframe.
        error (str, optional): Error message to be displayed if an exception occurs.
        graph_html (str, optional): HTML representation of the generated plot.
        selected_plot (str, optional): The type of plot selected by the user.
        selected_column1 (str, optional): The first column selected by the user for plotting.
        selected_column2 (str, optional): The second column selected by the user for plotting (if applicable).
    """
    global dataframe
    
    if dataframe is None:
        return HttpResponse("Aucune donnée n'a été chargée.")
    
    columns = dataframe.columns.tolist()
    numeric_columns = dataframe.select_dtypes(include=['number']).columns.tolist()
    
    if request.method == 'GET':
        context = {
            'columns': columns,
            'numeric_columns': numeric_columns
        }
        return render(request, 'visualize.html', context)
    
    try:
        plot_type = request.POST.get('plot_type', 'histogram')
        column1 = request.POST.get('column1')
        column2 = request.POST.get('column2')
        
        if not column1 and plot_type != 'correlation':
            context = {
                'columns': columns,
                'numeric_columns': numeric_columns,
                'error': "Veuillez sélectionner au moins une colonne."
            }
            return render(request, 'visualize.html', context)
        
        # Create the appropriate plot based on user input
        if plot_type == 'histogram':
            fig = px.histogram(dataframe, x=column1, nbins=30, title=f"Distribution de {column1}")
        elif plot_type == 'boxplot':
            fig = px.box(dataframe, y=column1, title=f"Box Plot de {column1}")
        elif plot_type == 'scatter':
            if not column2:
                raise ValueError("Veuillez sélectionner deux colonnes pour un graphique de dispersion.")
            fig = px.scatter(dataframe, x=column1, y=column2, title=f"{column1} vs {column2}")
        elif plot_type == 'bar':
            counts = dataframe[column1].value_counts().reset_index()
            counts.columns = ['index', column1]
            fig = px.bar(counts, x='index', y=column1, title=f"Diagramme en barres de {column1}")
        elif plot_type == 'correlation':
            numeric_cols = dataframe.select_dtypes(include=['number']).columns
            corr_matrix = dataframe[numeric_cols].corr()
            fig = px.imshow(corr_matrix, title="Matrice de corrélation", aspect='auto', color_continuous_scale='viridis')
        else:
            raise ValueError("Type de graphique non supporté.")
        
        # Add zoom and interaction enhancements
        fig.update_layout(
            dragmode='zoom',  # Enable zooming
            hovermode='closest',  # Highlight closest point on hover
            xaxis=dict(showgrid=True, zeroline=True),
            yaxis=dict(showgrid=True, zeroline=True),
        )
        
        # Return the plot as an HTML object
        graph_html = fig.to_html(full_html=False, config={
            'scrollZoom': True,  # Enable scroll zooming
            'displaylogo': False,  # Hide Plotly logo from mode bar
            'modeBarButtonsToRemove': ['lasso2d', 'select2d'],  # Remove lasso and selection tools if unnecessary
            'modeBarButtonsToAdd': ['zoomIn', 'zoomOut', 'resetScale'],  # Add zoom buttons
        })
        
        context = {
            'graph_html': graph_html,
            'columns': columns,
            'numeric_columns': numeric_columns,
            'selected_plot': plot_type,
            'selected_column1': column1,
            'selected_column2': column2
        }
        return render(request, 'visualize.html', context)
    
    except Exception as e:
        context = {
            'columns': columns,
            'numeric_columns': numeric_columns,
            'error': str(e)
        }
        return render(request, 'visualize.html', context)
