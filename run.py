from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo
from flask_bcrypt import Bcrypt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
from uuid import uuid4 
from io import BytesIO
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'my_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Ruta de la base de datos SQLite
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellido_paterno = db.Column(db.String(100), nullable=False)
    apellido_materno = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(15), nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False)
    laboratorio = db.Column(db.String(100), nullable=False)
    institucion = db.Column(db.String(100), nullable=False)
    contrasena = db.Column(db.String(100), nullable=False)

class RegistroForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    nombre = StringField('Nombre(s)', validators=[DataRequired()])
    apellido_paterno = StringField('Apellido paterno', validators=[DataRequired()])
    apellido_materno = StringField('Apellido materno', validators=[DataRequired()])
    telefono = StringField('Teléfono', validators=[DataRequired()])
    correo = StringField('Correo', validators=[DataRequired(), Email()])
    laboratorio = StringField('Laboratorio', validators=[DataRequired()])
    institucion = StringField('Institución', validators=[DataRequired()])
    contrasena = PasswordField('Contraseña', validators=[DataRequired()])
    verificacion_contrasena = PasswordField('Verificación de contraseña', validators=[DataRequired(), EqualTo('contrasena')])
    submit = SubmitField('Agregar registro')

# General Information
class GeneralInfoForm(FlaskForm):
    experiment_date = StringField('Fecha del experimento', validators=[DataRequired()])
    experiment_number = StringField('Número de experimento', validators=[DataRequired()])
    principal_investigator = StringField('Investigador principal', validators=[DataRequired()])
    institution_lab = StringField('Institución (y Laboratorio)', validators=[DataRequired()])
    submit = SubmitField('Enviar')

class GeneralInfoDataModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    experiment_date = db.Column(db.Date, nullable=False)
    experiment_number = db.Column(db.String(100), nullable=False)
    principal_investigator = db.Column(db.String(100), nullable=False)
    institution_lab = db.Column(db.String(100), nullable=False)

# Experimental Design
class ExperimentalDesignForm(FlaskForm):
    group_control_definition = StringField('Definición del grupo control', validators=[DataRequired()])
    group_experimental_definition = StringField('Definición del grupo experimental', validators=[DataRequired()])
    group_control_number = StringField('Número de grupo de control', validators=[DataRequired()])
    group_experimental_number = StringField('Número de grupo experimental', validators=[DataRequired()])
    submit = SubmitField('Enviar')
    
class DesignDataModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_control_definition = db.Column(db.String(100), nullable=False)
    group_experimental_definition = db.Column(db.String(100), nullable=False)
    group_control_number = db.Column(db.Integer, nullable=False)
    group_experimental_number = db.Column(db.Integer, nullable=False)
    
# Sample
class SampleForm(FlaskForm):
    sample_type_choices = [('ADN genómico', 'ADN genómico'), ('ARN total', 'ARN total'), ('Plasmidos', 'Plasmidos'), ('Cultivos celulares', 'Cultivos celulares'), ('Tejidos', 'Tejidos'), ('Sangre', 'Sangre'), ('Fuidos biologicos', 'Fuidos biologicos'), ('Tejidos vegetales', 'Tejidos vegetales'), ('Muestras ambientales', 'Muestras ambientales'), ('Tarjetas FTA', 'Tarjetas FTA')]
    sampling_procedure_choices = [('Microdisección', 'Microdisección'), ('Hisopado', 'Hisopado'), ('Micropunción', 'Micropunción'), ('Dilución seriada', 'Dilución seriada')]
    freezing_method_choices = [('Refrigeración 4°C','Refrigeración 4°C'), ('Refrigeración 8°C','Refrigeración 8°C'), ('Congelación -20°C','Congelación -20°C'), ('Ultracongelacion -70°C','Ultracongelacion -70°C'), ('Hielo seco -78.5°C','Hielo seco -78.5°C'), ('LiquidNitrogen','Nitrogeno Líquido -196°C')]
    sample_volume_mass_choices = [('<200 uL Microvolumen','<200 uL'),('>200 uL Macrovolumen','>200 uL'),('<200 ug Micromuestra','<200 ug'), (' >200 ug Macromuestra','>200 ug')]
    fixation_method_sample_choices = [('Ninguna','Ninguna'),('Formol','Formol'),('Tejido Embebido en Parafina','Tejido Embebido en Parafina (FFPE)'), ('Aerosol citológico (Cytospray)','Aerosol citológico')]
    storage_conditions_choices = [('Refrigeración 4°C','Refrigeración 4°C'), ('Refrigeración 8°C','Refrigeración 8°C'), ('Congelación -20°C','Congelación -20°C'), ('Ultracongelacion -70°C','Ultracongelacion -70°C'), ('Hielo Seco -78.5°C','Hielo Seco -78.5°C'), ('Nitrogeno líquido -196°C','Nitrogeno líquido -196°C')]


    sample_type = SelectField('Tipo de muestra', choices=sample_type_choices, validators=[DataRequired()], default='ADN')
    sample_description = TextAreaField('Descripción', validators=[DataRequired()])
    sample_volume_mass = SelectField('Volumen/Masa de la muestra procesada', choices=sample_volume_mass_choices, validators=[DataRequired()], default="Microvolumen")
    sampling_procedure = SelectField('Procedimiento de muestreo', choices=sampling_procedure_choices, validators=[DataRequired()], default='Micro')
    freezing_method = SelectField('Método de congelación', choices=freezing_method_choices, validators=[DataRequired()], default = "Enfriador4")
    fixation_method = SelectField('Método de fijación', choices=fixation_method_sample_choices, validators=[DataRequired()], default='Ninguno')
    storage_conditions = SelectField('Condiciones y duración de almacenamiento', choices=storage_conditions_choices, validators=[DataRequired()], default='Enfriador4')
    submit = SubmitField('Enviar')


class SampleDataModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sample_type = db.Column(db.String(100), nullable=False)
    sample_description = db.Column(db.Text, nullable=False)
    sample_volume_mass = db.Column(db.String(100), nullable=False)
    sampling_procedure = db.Column(db.String(100), nullable=False)
    freezing_method = db.Column(db.String(100), nullable=False)
    fixation_method = db.Column(db.String(100), nullable=False)
    storage_conditions = db.Column(db.String(100), nullable=False)

# NucleicAcidExtraction
class NucleicAcidExtractionForm(FlaskForm):
    extraction_procedure_choices = [
        ('Fenol/cloroformo/alcohol isoamílico (25:24:1)', 'Fenol/cloroformo/alcohol isoamílico (25:24:1)'),
        ('Trizol', 'Trizol'),
        ('Resina', 'Resina'),
        ('Columnas', 'Columnas'),
        ('Automática/Robóticas', 'Automática/Robóticas'),
        ('Magnética', 'Magnética')
    ]

    kit_details_choices = [
        ('ADN', 'ADN'),
        ('ARN', 'ARN'),
        ('ADN/ARN', 'ADN/ARN'),
        ('Plásmido', 'Plásmido'),
        ('Remoción de agarosa', 'Remoción de agarosa'),
        ('Remoción de parafina', 'Remoción de parafina')
    ]

    additional_reagents_choices = [
        ('Ninguno', 'Ninguno'),
        ('Optimizado en laboratorio', 'Optimizado en laboratorio')
    ]

    dnase_rnase_treatment_choices = [
        ('Ninguno', 'Ninguno'),
        ('Tratamiento con DNAsa', 'Tratamiento con DNAsa'),
        ('Tratamiento con RNAsa', 'Tratamiento con RNAsa')
    ]

    contamination_evaluation_choices = [
        ('C+, C-, NTC', 'C+, C-, NTC'),
        ('C+, C-', 'C+, C-'),
        ('Ninguno', 'Ninguno')
    ]

    nucleic_acid_quantification_method_choices = [
        ('Espectroscopía Ultravioleta UV', 'Espectroscopía Ultravioleta UV'),
        ('Espectroscopía de Fluorescencia', 'Espectroscopía de Fluorescencia'),
        ('Cuantificación en Nanodrop', 'Cuantificación en Nanodrop'),
        ('Cuantificación mediante gel de referencia', 'Cuantificación mediante gel de referencia'),
        ('Plásmido de referencia', 'Plásmido de referencia'),
        ('PCR cuantitativo', 'PCR cuantitativo'),
        ('PCR digital', 'PCR digital')
    ]

    nucleic_acid_purity_choices = [
        ('1.7-2.0','1.7-2.0'),
        ('<1.7','<1.7'),
        ('>2.0','>2.0'),
        ('Dato no disponible','Dato no disponible'),
    ]

    nucleic_acid_yield_choices = [
        ('Sin datos','Sin datos'),
        ('Inserte dato','Inserte dato'),
    ]

    integrity_assessment_method_choices = [
        ('Medidas espectrométricas', 'Medidas espectrométricas'),
        ('Electroforesis en gel', 'Electroforesis en gel'),
        ('Electroforesis capilar', 'Electroforesis capilar'),
        ('microfluidos', 'Microfluidos')
    ]

    electrophoresis_traces_choices = [
        ('No se observa degradación','No se observa degradación'),
        ('Baja degradación','Baja degradación'),
        ('Alta degradación','Alta degradación'),
        ('Degradación no comprobada','Degradación no comprobada'),
    ]

    inhibition_testing_choices = [
        ('Ninguno', 'Ninguno'),
        ('Prueba SPUD', 'Prueba SPUD'),
        ('Control endógeno', 'Control endógeno')
    ]

    extraction_procedure = SelectField('Procedimiento de extracción y/o instrumentación', 
                                       choices=extraction_procedure_choices,
                                       validators=[DataRequired()],
                                       default='organico')

    kit_details = SelectField('Detalles del kit y cualquier modificación', 
                              choices=kit_details_choices,
                              validators=[DataRequired()],
                              default='ADN')

    additional_reagents = SelectField('Fuente de reactivos adicionales utilizados', 
                                      choices=additional_reagents_choices,
                                      validators=[DataRequired()],
                                      default='Ninguno')

    dnase_rnase_treatment = SelectField('Detalles del tratamiento con DNAsa o RNAsa', 
                                         choices=dnase_rnase_treatment_choices,
                                         validators=[DataRequired()], 
                                         default='Ninguno')

    contamination_evaluation = SelectField('Evaluación de contaminación (DNA o RNA)', 
                                           choices=contamination_evaluation_choices,
                                           validators=[DataRequired()],
                                           default='Completo')

    nucleic_acid_quantification_method = SelectField('Método de cuantificación de ácidos nucleicos (Instrumento y método)', 
                                                     choices=nucleic_acid_quantification_method_choices,
                                                     validators=[DataRequired()],
                                                     default='UV')

    
    nucleic_acid_purity = SelectField('Pureza de ácido nucleico (A260/A280)', 
                                      choices=nucleic_acid_purity_choices,
                                      validators=[DataRequired()],
                                      default='Ninguno')


    nucleic_acid_yield = SelectField('Rendimiento de ácido nucleico', 
                                     choices=nucleic_acid_yield_choices,
                                     validators=[DataRequired()],
                                     default='Ninguno')

    rin_rqi_cq_details = StringField("RIN/RQI o Cq de transcripciones de 3' y 5'", validators=[DataRequired()])
    
    
    integrity_assessment_method = SelectField('Método de evaluación de integridad (RNA)', 
                                              choices=integrity_assessment_method_choices,
                                              validators=[DataRequired()],
                                              default='Espectrometrico')


    electrophoresis_traces = SelectField('Rastros de electroforesis', 
                                         choices=electrophoresis_traces_choices,
                                         validators=[DataRequired()],
                                         default='Ninguno')

    inhibition_testing = SelectField('Prueba de inhibición (Diluciones de Cq, picos u otros)', 
                                     choices=inhibition_testing_choices,
                                     validators=[DataRequired()],
                                     default='Endogeno')
    
    submit = SubmitField('Enviar')



class NucleicAcidExtractionDataModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    extraction_procedure = db.Column(db.String(100), nullable=False)
    kit_details = db.Column(db.String(100), nullable=False)
    additional_reagents = db.Column(db.String(100), nullable=False)
    dnase_rnase_treatment = db.Column(db.String(100), nullable=False)
    contamination_evaluation = db.Column(db.String(100), nullable=False)
    nucleic_acid_quantification_method = db.Column(db.String(100), nullable=False)
    nucleic_acid_purity = db.Column(db.String(100), nullable=False)
    nucleic_acid_yield = db.Column(db.String(100), nullable=False)
    integrity_assessment_method = db.Column(db.String(100), nullable=False)
    rin_rqi_cq_details = db.Column(db.String(100), nullable=False)
    electrophoresis_traces = db.Column(db.String(100), nullable=False)
    inhibition_testing = db.Column(db.String(100), nullable=False)

#Reverse Transcription
class ReverseTranscriptionForm(FlaskForm):

    # E - Condiciones completas de la reacción
    reaction_conditions = SelectField(
        label='Condiciones de Reacción',
        choices=[
            ('Protocolo de una etapa', 'Protocolo de una etapa'),
            ('Protocolo de dos etapas', 'Protocolo de dos etapas')
        ],
        validators=[DataRequired()],
        default='Protocolo de una etapa'
    )

    # E - Cantidad de ARN y volúmenes de reacción
    rna_quantity = StringField(
        label='Cantidad de ARN',
        validators=[DataRequired()]
    )

    reaction_volumes = StringField(
        label='Volúmenes de reacción',
        validators=[DataRequired()]
    )

    # E - Oligonucleótidos de cebado inverso (si se usa GSP) y concentración
    reverse_transcriptase_oligo_priming = SelectField(
        label='Oligonucleótidos de cebado inverso',
        choices=[
            ('Oligo dT18', 'Oligo dT18'),
            ('Primer hexamérico aleatorio (RHP)', 'Primer hexamérico aleatorio (RHP)'),
            ('Cebado específico del gen (GSP)', 'Cebado específico del gen (GSP)'),
            ('Mezcla de oligo dT18 y primer hexamérico aleatorio (dT18/RHP)', 'Mezcla de oligo dT18 y primer hexamérico aleatorio (dT18/RHP)')
        ],
        validators=[DataRequired()],
        default='Mezcla de oligo dT18 y primer hexamérico aleatorio (dT18/RHP)'
    )

    reverse_transcriptase_oligo_concentration = StringField(
        label='Concentración de oligonucleótidos de cebado inverso',
        validators=[DataRequired()]
    )

    # E - Transcriptasa inversa y concentración
    reverse_transcriptase_type = SelectField(
        label='Tipo de transcriptasa inversa',
        choices=[
            ('Virus de la Mieloblastosis Aviaria (AMV)', 'Virus de la Mieloblastosis Aviaria (AMV)'),
            ('Virus de la Leucemia Murina de Maloney (M-MLV)', 'Virus de la Leucemia Murina de Maloney (M-MLV)')
        ],
        validators=[DataRequired()],
        default='Virus de la Mieloblastosis Aviaria'
    )

    reverse_transcriptase_concentration = StringField(
        label='Concentración de transcriptasa inversa',
        validators=[DataRequired()]
    )

    # E - Temperatura y tiempo
    reverse_transcriptase_temperature = StringField(
        label='Temperatura de la transcriptasa inversa',
        validators=[DataRequired()]
    )

    reverse_transcriptase_reaction_time = StringField(
        label='Tiempo de reacción de la transcriptasa inversa',
        validators=[DataRequired()]
    )

    # D - Fabricante de reactivos y números de catálogo
    reverse_transcriptase_manufacturer = StringField(
        label='Fabricante de la transcriptasa inversa',
        validators=[DataRequired()]
    )

    reverse_transcriptase_catalog_number = StringField(
        label='Número de catálogo de la transcriptasa inversa',
        validators=[DataRequired()]
    )

    # D - Cqs con y sin transcripción inversa
    # Este parámetro se omitió

    # D - Condiciones de almacenamiento del cDNA
    cdna_storage_conditions = SelectField(
        label='Condiciones de almacenamiento del cDNA',
        choices=[
            ('Muestra de cDNA fresca', 'Muestra de cDNA fresca'),
            ('Noche a 4°C', 'Noche a 4°C'),
            ('Congelador a -20°C', 'Congelador a -20°C'),
            ('Ultracongelador a -80°C', 'Ultracongelador a -80°C')
        ],
        validators=[DataRequired()],
        default='Ninguno'
    )

    # Enviar
    Submit = SubmitField('Enviar')


class ReverseTranscriptionDataModel(db.Model):
    __tablename__ = 'reverse_transcription_data'  # Name of the table in the database

    id = db.Column(db.Integer, primary_key=True)
    reaction_conditions = db.Column(db.String(50), nullable=False)
    rna_quantity = db.Column(db.String(50), nullable=False)
    reaction_volumes = db.Column(db.String(50), nullable=False)
    reverse_transcriptase_oligo_priming = db.Column(db.String(50), nullable=False)
    reverse_transcriptase_oligo_concentration = db.Column(db.String(50), nullable=False)
    reverse_transcriptase_type = db.Column(db.String(50), nullable=False) 
    reverse_transcriptase_concentration = db.Column(db.String(50), nullable=False)  
    reverse_transcriptase_temperature = db.Column(db.String(50), nullable=False)
    reverse_transcriptase_reaction_time = db.Column(db.String(50), nullable=False)
    reverse_transcriptase_manufacturer = db.Column(db.String(50), nullable=False)
    reverse_transcriptase_catalog_number = db.Column(db.String(50), nullable=False)
    cdna_storage_conditions = db.Column(db.String(50), nullable=False)     


# Información del blanco de qPCR
class qPCRTargetInfoForm(FlaskForm):
    gene_symbol = StringField('Símbolo del gen', validators=[DataRequired()])
    multiplex_efficiency_lod = StringField('Eficiencia multiplex y LOD para cada ensayo', validators=[DataRequired()])
    sequence_accession_number = StringField('Número de acceso de la secuencia', validators=[DataRequired()])
    amplicon_location = StringField('Ubicación del amplicón', validators=[DataRequired()])
    amplicon_length = StringField('Longitud del amplicón', validators=[DataRequired()])
    in_silico_specificity_screening = StringField('Especificidad In Silico (BLAST, etc.)', validators=[DataRequired()])
    pseudogenes_homologs = StringField('Pseudogenes, Retropseudogenes u otros homólogos', validators=[DataRequired()])
    sequence_alignment = StringField('Alineamiento de secuencias', validators=[DataRequired()])
    amplicon_secondary_structure_analysis = StringField('Análisis de estructura secundaria del amplicón', validators=[DataRequired()])
    primer_location_exon_intron = StringField('Ubicación del cebador por exón o intron (si corresponde)', validators=[DataRequired()])
    splicing_variants_targeted = StringField('Variantes de empalme dirigidas', validators=[DataRequired()])
    submit = SubmitField('Enviar')

class qPCRTargetInfoDataModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gene_symbol = db.Column(db.String(100), nullable=False)
    multiplex_efficiency_lod = db.Column(db.String(100), nullable=False)
    sequence_accession_number = db.Column(db.String(100), nullable=False)
    amplicon_location = db.Column(db.String(100), nullable=False)
    amplicon_length = db.Column(db.String(100), nullable=False)
    in_silico_specificity_screening = db.Column(db.String(100), nullable=False)
    pseudogenes_homologs = db.Column(db.String(100), nullable=False)
    sequence_alignment = db.Column(db.String(100), nullable=False)
    amplicon_secondary_structure_analysis = db.Column(db.String(100), nullable=False)
    primer_location_exon_intron = db.Column(db.String(100), nullable=False)
    splicing_variants_targeted = db.Column(db.String(100), nullable=False)

# Primers de qPCR
class qPCRPrimersForm(FlaskForm):
    forward_sequence = StringField('Secuencia forward', validators=[DataRequired()])
    reverse_sequence = StringField('Secuencia reverse', validators=[DataRequired()])
    rtprimerdb_id = StringField('Número de identificación en RTPrimerDB', validators=[DataRequired()])
    probe_sequences = StringField('Secuencias de la sonda (si corresponde)')
    modification_location_identity = StringField('Ubicación e identidad de la modificación', validators=[DataRequired()])
    oligo_manufacturer = StringField('Fabricante del oligo', validators=[DataRequired()])
    purification_method = StringField('Método de purificación', validators=[DataRequired()])
    submit = SubmitField('Enviar')


class qPCRPrimersDataModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    forward_sequence = db.Column(db.String(100), nullable=False)
    reverse_sequence = db.Column(db.String(100), nullable=False)
    rtprimerdb_id = db.Column(db.String(100), nullable=False)
    probe_sequences = db.Column(db.String(100))
    modification_location_identity = db.Column(db.String(100), nullable=False)
    oligo_manufacturer = db.Column(db.String(100), nullable=False)
    purification_method = db.Column(db.String(100), nullable=False)

# qPCR Protocol
# Formulario de Protocolo de qPCR
class qPCRProtocolForm(FlaskForm):
    reaction_conditions = StringField('Condiciones de reacción', validators=[DataRequired()])
    reaction_volume_dna_quantity = StringField('Volumen de reacción y cantidad de ADN', validators=[DataRequired()])
    primer_probe_concentrations = StringField('Concentraciones de cebadores, sondas, Mg++ y dNTP', validators=[DataRequired()])
    polymerase_identity_concentration = StringField('Identidad y concentración de la polimerasa', validators=[DataRequired()])
    buffer_kit_identity_manufacturer = StringField('Identidad del buffer/kit y fabricante', validators=[DataRequired()])
    buffer_exact_chemical_constitution = StringField('Constitución química exacta del buffer', validators=[DataRequired()])
    additives = StringField('Aditivos (SYBR Green I, DMSO, etc.)', validators=[DataRequired()])
    plates_tubes_manufacturer_catalog = StringField('Fabricante y número de catálogo de placas/tubos', validators=[DataRequired()])
    thermocycling_parameters = StringField('Parámetros de termociclado', validators=[DataRequired()])
    reaction_configuration = StringField('Configuración de la reacción (manual/automática)', validators=[DataRequired()])
    qpcr_instrument_manufacturer = StringField('Fabricante del instrumento de qPCR', validators=[DataRequired()])
    reaction_quality_control = StringField('Control de calidad de la reacción', validators=[DataRequired()])
    submit = SubmitField('Enviar')

class qPCRProtocolDataModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reaction_conditions = db.Column(db.String(100), nullable=False)
    reaction_volume_dna_quantity = db.Column(db.String(100), nullable=False)
    primer_probe_concentrations = db.Column(db.String(100), nullable=False)
    polymerase_identity_concentration = db.Column(db.String(100), nullable=False)
    buffer_kit_identity_manufacturer = db.Column(db.String(100), nullable=False)
    buffer_exact_chemical_constitution = db.Column(db.String(100), nullable=False)
    additives = db.Column(db.String(100), nullable=False)
    plates_tubes_manufacturer_catalog = db.Column(db.String(100), nullable=False)
    thermocycling_parameters = db.Column(db.String(100), nullable=False)
    reaction_configuration = db.Column(db.String(100), nullable=False)
    qpcr_instrument_manufacturer = db.Column(db.String(100), nullable=False)
    reaction_quality_control = db.Column(db.String(100), nullable=False)

# Data Analysis
class DataAnalysisForm(FlaskForm):
    qpcr_analysis_program = StringField('Programa de análisis de qPCR (fuente, versión)', validators=[DataRequired()])
    cq_method_determination = StringField('Determinación del método Cq', validators=[DataRequired()])
    identification_handling_outliers = StringField('Identificación y manejo de valores atípicos', validators=[DataRequired()])
    ntc_results = StringField('Resultados NTC', validators=[DataRequired()])
    reference_genes_justification = StringField('Justificación del número y elección de genes de referencia', validators=[DataRequired()])
    normalization_method_description = StringField('Descripción del método de normalización', validators=[DataRequired()])
    biological_replicates_number_concordance = StringField('Número y concordancia de repeticiones biológicas', validators=[DataRequired()])
    technical_replicates_number_stage = StringField('Número y etapa (RT o qPCR) de repeticiones técnicas', validators=[DataRequired()])
    intra_assay_variation_repeatability = StringField('Repetibilidad (Variación Intra-Ensayo)', validators=[DataRequired()])
    inter_assay_variation_reproducibility = StringField('Reproducibilidad (Variación Inter-Ensayo, %CV)', validators=[DataRequired()])
    power_analysis = StringField('Análisis de potencia', validators=[DataRequired()])
    statistical_methods_significance = StringField('Métodos estadísticos para la significancia de los resultados', validators=[DataRequired()])
    software_source_version = StringField('Software (fuente, versión)', validators=[DataRequired()])
    cq_or_raw_data_rdml_submission = StringField('Envío de datos Cq o datos crudos usando RDML', validators=[DataRequired()])
    submit = SubmitField('Enviar')

class DataAnalysisModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    qpcr_analysis_program = db.Column(db.String(255), nullable=False)
    cq_method_determination = db.Column(db.String(255), nullable=False)
    identification_handling_outliers = db.Column(db.String(255), nullable=False)
    ntc_results = db.Column(db.String(255), nullable=False)
    reference_genes_justification = db.Column(db.String(255), nullable=False)
    normalization_method_description = db.Column(db.String(255), nullable=False)
    biological_replicates_number_concordance = db.Column(db.String(255), nullable=False)
    technical_replicates_number_stage = db.Column(db.String(255), nullable=False)
    intra_assay_variation_repeatability = db.Column(db.String(255), nullable=False)
    inter_assay_variation_reproducibility = db.Column(db.String(255), nullable=False)
    power_analysis = db.Column(db.String(255), nullable=False)
    statistical_methods_significance = db.Column(db.String(255), nullable=False)
    software_source_version = db.Column(db.String(255), nullable=False)
    cq_or_raw_data_rdml_submission = db.Column(db.String(255), nullable=False)

# Thermal Cycling Conditions
class ThermalCyclingConditionsForm(FlaskForm):
    equipment_used = StringField('Equipo utilizado', validators=[DataRequired()])
    primers_used = StringField('Cebadores utilizados', validators=[DataRequired()])
    pcr_conditions = StringField('Condiciones de PCR: Número de ciclos/Temperatura de desnaturalización/Temperatura de alineamiento/Temperatura de extensión', validators=[DataRequired()])
    reaction_volume = StringField('Volumen de reacción', validators=[DataRequired()])
    positive_control = StringField('Control positivo', validators=[DataRequired()])
    negative_control = StringField('Control negativo', validators=[DataRequired()])
    submit = SubmitField('Enviar')

class ThermalCyclingConditionsDataModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipment_used = db.Column(db.String(100), nullable=False)
    primers_used = db.Column(db.String(100), nullable=False)
    pcr_conditions = db.Column(db.String(100), nullable=False)
    reaction_volume = db.Column(db.String(100), nullable=False)
    positive_control = db.Column(db.String(100), nullable=False)
    negative_control = db.Column(db.String(100), nullable=False)

# qPCR Validation
class qPCRValidationForm(FlaskForm):
    optimization_evidence = StringField('Evidencia de optimización (a partir de gradientes)', validators=[DataRequired()])
    specificity_evidence = StringField('Evidencia de especificidad (gel, secuencia, fusión o digestión)', validators=[DataRequired()])
    cq_nct_for_sybr_green = StringField('Para SYBR Green I, Cq de NCT', validators=[DataRequired()])
    standard_curves_slope_intercept = StringField('Curvas estándar con pendiente e intercepto', validators=[DataRequired()])
    pcr_efficiency_slope_calculation = StringField('Eficiencia de PCR calculada a partir de la pendiente', validators=[DataRequired()])
    pcr_efficiency_confidence_interval = StringField('Intervalo de confianza para la eficiencia de PCR', validators=[DataRequired()])
    r2_standard_curve = StringField('R^2 de la curva estándar', validators=[DataRequired()])
    linear_dynamic_range = StringField('Rango dinámico lineal', validators=[DataRequired()])
    cq_variation_lower_limit = StringField('Variación de Cq en el límite inferior', validators=[DataRequired()])
    confidence_intervals_full_range = StringField('Intervalos de confianza en todo el rango', validators=[DataRequired()])
    lod_evidence = StringField('Evidencia de LOD', validators=[DataRequired()])
    multiplex_efficiency_lod = StringField('Si es multiplex, eficiencia y LOD para cada ensayo', validators=[DataRequired()])
    submit = SubmitField('Enviar')


class qPCRValidationDataModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    optimization_evidence = db.Column(db.String(100), nullable=False)
    specificity_evidence = db.Column(db.String(100), nullable=False)
    cq_nct_for_sybr_green = db.Column(db.String(100), nullable=False)
    standard_curves_slope_intercept = db.Column(db.String(100), nullable=False)
    pcr_efficiency_slope_calculation = db.Column(db.String(100), nullable=False)
    pcr_efficiency_confidence_interval = db.Column(db.String(100), nullable=False)
    r2_standard_curve = db.Column(db.String(100), nullable=False)
    linear_dynamic_range = db.Column(db.String(100), nullable=False)
    cq_variation_lower_limit = db.Column(db.String(100), nullable=False)
    confidence_intervals_full_range = db.Column(db.String(100), nullable=False)
    lod_evidence = db.Column(db.String(100), nullable=False)
    multiplex_efficiency_lod = db.Column(db.String(100), nullable=False)

# Real-Time PCR Data
class RealTimePCRDataForm(FlaskForm):
    data_analysis_software = StringField('Software de análisis de datos', validators=[DataRequired()])
    quantification_method = StringField('Método de cuantificación', validators=[DataRequired()])
    raw_data = StringField('Datos Crudos: Ciclo de umbral (Ct): Gen deseado (nombre y valor de Ct) / Gen de referencia (nombre y valor de Ct); Eficiencia de amplificación', validators=[DataRequired()])
    submit = SubmitField('Enviar')


class RealTimePCRDataModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_analysis_software = db.Column(db.String(255), nullable=False)
    quantification_method = db.Column(db.String(255), nullable=False)
    raw_data = db.Column(db.String(255), nullable=False)


# Results and Analysis
class ResultsAnalysisForm(FlaskForm):
    results_interpretation = StringField('Interpretación de resultados', validators=[DataRequired()])
    charts_figures = StringField('Gráficos y figuras (incluye gráficos de amplificación y otros datos relevantes)', validators=[DataRequired()])
    submit = SubmitField('Enviar')


class ResultsAnalysisModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    results_interpretation = db.Column(db.String(255), nullable=False)
    charts_figures = db.Column(db.String(255), nullable=False)


class Informe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    experiment_date = db.Column(db.DateTime, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)  # Nombre correcto de la columna
    principal_investigator = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'Informe {self.id} - {self.experiment_date}'




# Crear las tablas dentro del contexto de la aplicación
with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return render_template('index.html')


# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Busca el usuario en la base de datos por nombre de usuario
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.contrasena, password):
            # Si las credenciales son válidas, establece la sesión del usuario
            session['username'] = user.username
            # Redirige al usuario al dashboard después de iniciar sesión
            return redirect(url_for('inicio'))
        else:
            # Si las credenciales no son válidas, muestra un mensaje de error
            error_msg = "Nombre de usuario o contraseña incorrectos. Intenta de nuevo."
            return render_template('login.html', error=error_msg)

    # Renderiza el formulario de inicio de sesión
    return render_template('login.html')


# Nueva ruta para el dashboard
@app.route('/dashboard')
def dashboard():
    # Verifica si el usuario ha iniciado sesión
    if 'username' in session:
        return render_template('dashboard.html')
    else:
        # Si el usuario no ha iniciado sesión, redirige al inicio de sesión
        return redirect(url_for('login'))

# LOGOUT
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

# INICIO
@app.route('/inicio')
def inicio():
    return render_template('inicio.html')

# ABOUT
@app.route('/about')
def about():
    return render_template('about.html')

# CONTACT
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Directorio donde se guardarán las imágenes de perfil
UPLOAD_FOLDER = 'path/to/upload/folder'  # Cambia esto por la ruta donde desees guardar las imágenes
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """ Verifica si la extensión del archivo es válida """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Register
@app.route('/register', methods=['GET', 'POST']) 
def register():
    form = RegistroForm()
    if form.validate_on_submit():
        try:
            hashed_password = bcrypt.generate_password_hash(form.contrasena.data).decode('utf-8')
            usuario = User(username=form.username.data, 
                           nombre=form.nombre.data,
                           apellido_paterno=form.apellido_paterno.data,
                           apellido_materno=form.apellido_materno.data,
                           telefono=form.telefono.data,
                           correo=form.correo.data,
                           laboratorio=form.laboratorio.data,
                           institucion=form.institucion.data,
                           contrasena=hashed_password)
            db.session.add(usuario)
            db.session.commit()
            return redirect(url_for('login'))
        except Exception as e:
            return render_template('error.html', error=str(e))
    return render_template('register.html', form=form)

# Profile
@app.route('/profile')
def profile():
    try:
        if 'username' in session:
            username = session['username']
            user = User.query.filter_by(username=username).first()
            if user:
                nombre = user.nombre
                apellido_paterno = user.apellido_paterno
                apellido_materno = user.apellido_materno
                telefono = user.telefono
                correo = user.correo
                laboratorio = user.laboratorio
                institucion = user.institucion

                return render_template('profile.html', username=username, nombre=nombre, apellido_paterno=apellido_paterno, apellido_materno=apellido_materno, telefono=telefono, correo=correo, laboratorio=laboratorio, institucion=institucion)
            else:
                flash('No se encontró información del usuario', 'warning')
                return redirect(url_for('index'))
        else:
            return redirect(url_for('index'))
    except Exception as e:
        return render_template('error.html', error=str(e))

# General Information
def get_auto_general_info_data():
    experiment_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    experiment_number = str(uuid4())
    principal_investigator = ""
    institution_lab = ""

    if 'username' in session:
        username = session['username']
        user = User.query.filter_by(username=username).first()
        if user:
            principal_investigator = f"{user.nombre} {user.apellido_paterno} {user.apellido_materno}"
            institution_lab = f"{user.laboratorio}, {user.institucion}"

    return experiment_date, experiment_number, principal_investigator, institution_lab

# Route to handle General Information form
@app.route('/info', methods=['GET', 'POST'])
def info():
    form = GeneralInfoForm()

    if form.validate_on_submit():
        try:
            # Get the experiment_date as a date object
            experiment_date_str = form.experiment_date.data
            experiment_date = datetime.strptime(experiment_date_str, '%Y-%m-%d %H:%M:%S')

            # Create GeneralInfoDataModel instance
            general_info_data = GeneralInfoDataModel(
                experiment_date=experiment_date,
                experiment_number=form.experiment_number.data,
                principal_investigator=form.principal_investigator.data,
                institution_lab=form.institution_lab.data
            )

            # Add to database and commit
            db.session.add(general_info_data)
            db.session.commit()

            flash('General information successfully recorded!', 'success')
            return redirect(url_for('design'))
        except Exception as e:
            flash(f'An error occurred while recording general information: {str(e)}', 'danger')

    if request.method == 'GET':
        try:
            auto_data = get_auto_general_info_data()
            form.experiment_date.data = auto_data[0]
            form.experiment_number.data = auto_data[1]
            form.principal_investigator.data = auto_data[2]
            form.institution_lab.data = auto_data[3]
        except Exception as e:
            flash(f'An error occurred while fetching automatic data: {str(e)}', 'danger')

    return render_template('info.html', form=form)

# Experimental Design
@app.route('/design', methods=['GET', 'POST'])
def design():
 if 'username' in session:
    form = ExperimentalDesignForm()
    if form.validate_on_submit():
        try:
    
            design_data = DesignDataModel(
                group_control_definition=form.group_control_definition.data,
                group_experimental_definition=form.group_experimental_definition.data,
                group_control_number=form.group_control_number.data,
                group_experimental_number=form.group_experimental_number.data
            )
            db.session.add(design_data)
            db.session.commit()
        except Exception as e:
            return render_template('error.html', error=str(e))

        return redirect(url_for('sample'))
    return render_template('design.html', form=form)

# Sample
@app.route('/sample', methods=['GET', 'POST'])
def sample():
   if 'username' in session: 
    form = SampleForm()
    if form.validate_on_submit():
        try:

            sample_data = SampleDataModel(
                sample_type=form.sample_type.data,
                sample_description=form.sample_description.data,
                sample_volume_mass=form.sample_volume_mass.data,
                sampling_procedure=form.sampling_procedure.data,
                freezing_method=form.freezing_method.data,
                fixation_method=form.fixation_method.data,
                storage_conditions=form.storage_conditions.data
            )
            db.session.add(sample_data)
            db.session.commit()
        except Exception as e:
            return render_template('error.html', error=str(e))

        return redirect(url_for('extraction'))
    return render_template('sample.html', form=form)

# Extracción de Ácido Nucleico
@app.route('/extraction', methods=['GET', 'POST'])
def extraction():
 if 'username' in session:
    form = NucleicAcidExtractionForm()
    if form.validate_on_submit():
        try:
            extraction_data = NucleicAcidExtractionDataModel(
                extraction_procedure=form.extraction_procedure.data,
                kit_details=form.kit_details.data,
                additional_reagents=form.additional_reagents.data,
                dnase_rnase_treatment=form.dnase_rnase_treatment.data,
                contamination_evaluation=form.contamination_evaluation.data,
                nucleic_acid_quantification_method=form.nucleic_acid_quantification_method.data,
                nucleic_acid_purity=form.nucleic_acid_purity.data,
                nucleic_acid_yield=form.nucleic_acid_yield.data,
                integrity_assessment_method=form.integrity_assessment_method.data,
                rin_rqi_cq_details=form.rin_rqi_cq_details.data,
                electrophoresis_traces=form.electrophoresis_traces.data,
                inhibition_testing=form.inhibition_testing.data
            )
            db.session.add(extraction_data)
            db.session.commit()
        except Exception as e:
            return render_template('error.html', error=str(e))

        return redirect(url_for('reverse'))
    return render_template('extraction.html', form=form)

#Reverse Transcription
@app.route('/reverse', methods=['GET', 'POST'])
def reverse():
    form = ReverseTranscriptionForm()
    if form.validate_on_submit():
        try:
            reverse_transcription_data = ReverseTranscriptionDataModel(
                reaction_conditions=form.reaction_conditions.data,
                rna_quantity=form.rna_quantity.data,
                reaction_volumes=form.reaction_volumes.data,
                reverse_transcriptase_oligo_priming=form.reverse_transcriptase_oligo_priming.data,
                reverse_transcriptase_oligo_concentration=form.reverse_transcriptase_oligo_concentration.data,
                reverse_transcriptase_type=form.reverse_transcriptase_type.data,
                reverse_transcriptase_concentration=form.reverse_transcriptase_concentration.data,
                reverse_transcriptase_temperature=form.reverse_transcriptase_temperature.data,
                reverse_transcriptase_reaction_time=form.reverse_transcriptase_reaction_time.data,
                reverse_transcriptase_manufacturer=form.reverse_transcriptase_manufacturer.data,
                reverse_transcriptase_catalog_number=form.reverse_transcriptase_catalog_number.data,
                cdna_storage_conditions=form.cdna_storage_conditions.data
            )
            db.session.add(reverse_transcription_data)
            db.session.commit()
        except Exception as e:
            return render_template('error.html', error=str(e))
        
        return redirect(url_for('target')) 
    
    return render_template('reverse.html', form=form)


# qPCR Target Information
@app.route('/target', methods=['GET', 'POST'])
def target():
   if 'username' in session:
    form = qPCRTargetInfoForm()
    if form.validate_on_submit():
        try:
            target_info_data = qPCRTargetInfoDataModel(
                gene_symbol=form.gene_symbol.data,
                multiplex_efficiency_lod=form.multiplex_efficiency_lod.data,
                sequence_accession_number=form.sequence_accession_number.data,
                amplicon_location=form.amplicon_location.data,
                amplicon_length=form.amplicon_length.data,
                in_silico_specificity_screening=form.in_silico_specificity_screening.data,
                pseudogenes_homologs=form.pseudogenes_homologs.data,
                sequence_alignment=form.sequence_alignment.data,
                amplicon_secondary_structure_analysis=form.amplicon_secondary_structure_analysis.data,
                primer_location_exon_intron=form.primer_location_exon_intron.data,
                splicing_variants_targeted=form.splicing_variants_targeted.data
            )
            db.session.add(target_info_data)
            db.session.commit()
        except Exception as e:
            return render_template('error.html', error=str(e))

        return redirect(url_for('oligo'))
    return render_template('target.html', form=form)


# qPCR Primers
@app.route('/oligo', methods=['GET', 'POST'])
def oligo():
   if 'username' in session:
    form = qPCRPrimersForm()
    if form.validate_on_submit():
        try:
            qpcr_primer_data = qPCRPrimersDataModel(
                forward_sequence=form.forward_sequence.data,
                reverse_sequence=form.reverse_sequence.data,
                rtprimerdb_id=form.rtprimerdb_id.data,
                probe_sequences=form.probe_sequences.data,
                modification_location_identity=form.modification_location_identity.data,
                oligo_manufacturer=form.oligo_manufacturer.data,
                purification_method=form.purification_method.data
            )
            db.session.add(qpcr_primer_data)
            db.session.commit()
        except Exception as e:
            return render_template('error.html', error=str(e))

        return redirect(url_for('protocol'))
    return render_template('oligo.html', form=form)

# qPCR Protocol
@app.route('/protocol', methods=['GET', 'POST'])
def protocol():
   if 'username' in session:
    form = qPCRProtocolForm()
    if form.validate_on_submit():
        try:
            protocol_data = qPCRProtocolDataModel(
                reaction_conditions=form.reaction_conditions.data,
                reaction_volume_dna_quantity=form.reaction_volume_dna_quantity.data,
                primer_probe_concentrations=form.primer_probe_concentrations.data,
                polymerase_identity_concentration=form.polymerase_identity_concentration.data,
                buffer_kit_identity_manufacturer=form.buffer_kit_identity_manufacturer.data,
                buffer_exact_chemical_constitution=form.buffer_exact_chemical_constitution.data,
                additives=form.additives.data,
                plates_tubes_manufacturer_catalog=form.plates_tubes_manufacturer_catalog.data,
                thermocycling_parameters=form.thermocycling_parameters.data,
                reaction_configuration=form.reaction_configuration.data,
                qpcr_instrument_manufacturer=form.qpcr_instrument_manufacturer.data,
                reaction_quality_control=form.reaction_quality_control.data
            )
            db.session.add(protocol_data)
            db.session.commit()
        except Exception as e:
            return render_template('error.html', error=str(e))

        return redirect(url_for('validation'))
    return render_template('protocol.html', form=form)

# Data Analysis
@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
   if 'username' in session:
    form = DataAnalysisForm()
    if form.validate_on_submit():
        try:
            data_analysis = DataAnalysisModel(
                qpcr_analysis_program=form.qpcr_analysis_program.data,
                cq_method_determination=form.cq_method_determination.data,
                identification_handling_outliers=form.identification_handling_outliers.data,
                ntc_results=form.ntc_results.data,
                reference_genes_justification=form.reference_genes_justification.data,
                normalization_method_description=form.normalization_method_description.data,
                biological_replicates_number_concordance=form.biological_replicates_number_concordance.data,
                technical_replicates_number_stage=form.technical_replicates_number_stage.data,
                intra_assay_variation_repeatability=form.intra_assay_variation_repeatability.data,
                inter_assay_variation_reproducibility=form.inter_assay_variation_reproducibility.data,
                power_analysis=form.power_analysis.data,
                statistical_methods_significance=form.statistical_methods_significance.data,
                software_source_version=form.software_source_version.data,
                cq_or_raw_data_rdml_submission=form.cq_or_raw_data_rdml_submission.data
            )
            db.session.add(data_analysis)
            db.session.commit()
            flash('Data analysis information has been successfully submitted.', 'success')
            return redirect(url_for('cycling'))
        except Exception as e:
            flash('An error occurred while processing your request. Please try again.', 'error')
            print(str(e))
            db.session.rollback()
    return render_template('analyze.html', form=form)

# Thermal Cycling Conditions
@app.route('/cycling', methods=['GET', 'POST'])
def cycling():
   if 'username' in session:
    form = ThermalCyclingConditionsForm()
    if form.validate_on_submit():
        try:
            thermal_data = ThermalCyclingConditionsDataModel(
                equipment_used=form.equipment_used.data,
                primers_used=form.primers_used.data,
                pcr_conditions=form.pcr_conditions.data,
                reaction_volume=form.reaction_volume.data,
                positive_control=form.positive_control.data,
                negative_control=form.negative_control.data
            )
            db.session.add(thermal_data)
            db.session.commit()
        except Exception as e:
            return render_template('error.html', error=str(e))

        return redirect(url_for('data'))
    return render_template('cycling.html', form=form)

# qPCR Validation
@app.route('/validation', methods=['GET', 'POST'])
def validation():
   if 'username' in session:
    form = qPCRValidationForm()
    if form.validate_on_submit():
        try:
            validation_data = qPCRValidationDataModel(
                optimization_evidence=form.optimization_evidence.data,
                specificity_evidence=form.specificity_evidence.data,
                cq_nct_for_sybr_green=form.cq_nct_for_sybr_green.data,
                standard_curves_slope_intercept=form.standard_curves_slope_intercept.data,
                pcr_efficiency_slope_calculation=form.pcr_efficiency_slope_calculation.data,
                pcr_efficiency_confidence_interval=form.pcr_efficiency_confidence_interval.data,
                r2_standard_curve=form.r2_standard_curve.data,
                linear_dynamic_range=form.linear_dynamic_range.data,
                cq_variation_lower_limit=form.cq_variation_lower_limit.data,
                confidence_intervals_full_range=form.confidence_intervals_full_range.data,
                lod_evidence=form.lod_evidence.data,
                multiplex_efficiency_lod=form.multiplex_efficiency_lod.data
            )
            db.session.add(validation_data)
            db.session.commit()
            flash('Datos de validación de qPCR agregados exitosamente', 'success')
            return redirect(url_for('analyze'))
        except Exception as e:
            flash('Error al agregar los datos de validación de qPCR: ' + str(e), 'danger')

    return render_template('validation.html', form=form)

# Real-Time PCR Data
@app.route('/data', methods=['GET', 'POST'])
def data():
   if 'username' in session:
    form = RealTimePCRDataForm()
    if form.validate_on_submit():
        try:
            realtime_pcr_data = RealTimePCRDataModel(
                data_analysis_software=form.data_analysis_software.data,
                quantification_method=form.quantification_method.data,
                raw_data=form.raw_data.data
            )
            db.session.add(realtime_pcr_data)
            db.session.commit()
            flash('Real-Time PCR data submitted successfully', 'success')
            return redirect(url_for('results'))
        except Exception as e:
            flash(f'An error occurred while submitting Real-Time PCR data: {str(e)}', 'danger')
            return render_template('error.html', error=str(e))

    return render_template('data.html', form=form)

# Results and Analysis
@app.route('/results', methods=['GET', 'POST'])
def results():
   if 'username' in session:
    form = ResultsAnalysisForm()
    if form.validate_on_submit():
        try:
            results_data = ResultsAnalysisModel(
                results_interpretation=form.results_interpretation.data,
                charts_figures=form.charts_figures.data
            )
            db.session.add(results_data)
            db.session.commit()
        except Exception as e:
            return render_template('error.html', error=str(e))

        return redirect(url_for('report'))
    return render_template('results.html', form=form)

# Report
@app.route('/report')
def report():
    if 'username' in session:
        username = session['username']
        general_info_data = GeneralInfoDataModel.query.all()
        design_data = DesignDataModel.query.all()
        sample_data = SampleDataModel.query.all()
        extraction_data = NucleicAcidExtractionDataModel.query.all()
        reverse_transcription_data = ReverseTranscriptionDataModel.query.all() 
        target_data = qPCRTargetInfoDataModel.query.all()  # Modelo de datos para qPCR Target Information
        primer_data = qPCRPrimersDataModel.query.all()  # Modelo de datos para qPCR Primers
        protocol_data = qPCRProtocolDataModel.query.all()
        thermal_data = ThermalCyclingConditionsDataModel.query.all()
        validation_data = qPCRValidationDataModel.query.all()
        data_analysis_data = DataAnalysisModel.query.all()
        results_data = ResultsAnalysisModel.query.all()
        real_time_pcr_data = RealTimePCRDataModel.query.all()
        return render_template('report.html', username=username, general_info_data=general_info_data, design_data=design_data, sample_data=sample_data, extraction_data=extraction_data, reverse_transcription_data=reverse_transcription_data, target_data=target_data, primer_data=primer_data, protocol_data=protocol_data, thermal_data=thermal_data, validation_data=validation_data, data_analysis_data=data_analysis_data, results_data=results_data, real_time_pcr_data=real_time_pcr_data)
    else:
        # Manejo si el usuario no ha iniciado sesión
        return redirect(url_for('login'))


@app.route('/guardar_informe', methods=['POST'])
def guardar_informe():
    if request.method == 'POST':
        contenido = request.form['contenido']
        autor = request.form['autor']

        nuevo_informe = Informe(contenido=contenido, autor=autor)

        try:
            db.session.add(nuevo_informe)
            db.session.commit()
            return redirect(url_for('mostrar_informes'))  # Redirige a la lista de informes
        except Exception as e:
            return f'Error al guardar el informe: {str(e)}', 500

    return 'Método no permitido', 405



@app.route('/informes')
def informes():
    # Obtener todos los informes de la base de datos
    informes = Informe.query.all()
    return render_template('informes.html', informes=informes)


@app.route('/ver_informe/<int:informe_id>')
def ver_informe(informe_id):
    # Obtener el informe de la base de datos por su ID
    informe = Informe.query.get_or_404(informe_id)
    return render_template('ver_informe.html', informe=informe)











#  Generar PDF
@app.route('/generate_pdf')
def generate_pdf():
    datos_general = GeneralInfoDataModel.query.first()
    #PODEMOS AGREGAR QUERY.FIRST (PARA AGREGAR SOLO LA PRIMERA INFO)
    #O QUERY.ALL (PARA AGREGAR TODA LA INFO DE LA BASE DE DATOS)
    datos_experimento = DesignDataModel.query.all()
    datos_muestra = SampleDataModel.query.all()
    datos_extraction = NucleicAcidExtractionDataModel.query.all()
    datos_reverse_transcription = ReverseTranscriptionDataModel.query.all()  
    datos_qpcr_target = qPCRTargetInfoDataModel.query.all()
    datos_qpcr_primers = qPCRPrimersDataModel.query.all()
    datos_qpcr_protocol = qPCRProtocolDataModel.query.all()
    datos_data_analysis = DataAnalysisModel.query.all()
    datos_thermal_cycling_conditions = ThermalCyclingConditionsDataModel.query.all()
    datos_qpcr_validation = qPCRValidationDataModel.query.all()
    datos_realtime_pcr_data = RealTimePCRDataModel.query.all()
    datos_results_analysis = ResultsAnalysisModel.query.all()

    # Crear un buffer de bytes para guardar el PDF generado
    buffer = BytesIO()

    # Crear un lienzo PDF
    c = canvas.Canvas(buffer, pagesize=letter)

    
    title = "INFORME DEL EXPERIMENTO"
    c.setFont("Helvetica-Bold", 20)
    title_width = c.stringWidth(title)
    title_x = (c._pagesize[0] - title_width) / 2
    title_y = c._pagesize[1] - 100  # Altura desde la parte superior de la página
    title_y += 50  # Añadir espacio adicional entre el título y el primer módulo

    # Dibujar el título centrado
    c.drawString(title_x, title_y, title)
    

    # Establecer posición inicial para los datos
    y_position = 700

    # Función para agregar una nueva página
    def add_new_page():
        c.showPage()
        c.setFont("Helvetica-Bold", 16)
        return 750

    # Agregar módulo de información general
    general_module_title = "Información General"
    c.setFont("Helvetica-Bold", 16)  # Configurar fuente en negrita
    c.drawString(100, y_position, general_module_title)

    c.setFont("Helvetica", 12)
    c.drawString(100, y_position - 20, f"Fecha del Experimento: {datos_general.experiment_date}")
    c.drawString(100, y_position - 40, f"Número del Experimento: {datos_general.experiment_number}")
    c.drawString(100, y_position - 60, f"Investigador Principal: {datos_general.principal_investigator}")
    c.drawString(100, y_position - 80, f"Institución (y Laboratorio): {datos_general.institution_lab}")
    y_position -= 80  # Bajar la posición después de cada conjunto de datos del experimento
    y_position -= 20  # Espacio vertical adicional entre cada conjunto de datos del experimento


    # Espacio vertical adicional antes de la sección de Datos del Experimento
    if y_position < 100:
        y_position = add_new_page()
    else:
        y_position -= 25  # Ajuste para agregar espacio entre secciones

    # Agregar título del módulo "Datos del Experimento"
    module_title = "Datos del Experimento"
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, y_position, module_title)
    y_position -= 20  # Bajar la posición después del título

    # Agregar datos de cada experimento
    for dato in datos_experimento:
        if y_position < 200:
         y_position = add_new_page()
        c.setFont("Helvetica", 12)  # Configurar fuente normal
        c.drawString(100, y_position, f"Definición del Grupo Control: {dato.group_control_definition}")
        y_position -= 20  # Bajar la posición después de cada conjunto de datos del experimento
        c.drawString(100, y_position, f"Definición del Grupo Experimental: {dato.group_experimental_definition}")
        y_position -= 20  # Bajar la posición después de cada conjunto de datos del experimento
        c.drawString(100, y_position, f"Número de Grupo Control: {dato.group_control_number}")
        y_position -= 20  # Bajar la posición después de cada conjunto de datos del experimento
        c.drawString(100, y_position, f"Número de Grupo Experimental: {dato.group_experimental_number}")
        y_position -= 40  # Bajar la posición después de cada conjunto de datos del experimento y agregar espacio adicional



    # Espacio vertical adicional antes de la sección de Muestra
    if y_position < 200:
        y_position = add_new_page()
    else:
        y_position -= 25  # Ajuste para agregar espacio entre secciones
    
    # Agregar módulo de muestra
    sample_module_title = "Muestra"
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, y_position, sample_module_title)
    y_position -= 20  # Bajar la posición después del título

    for muestra in datos_muestra:
     if y_position < 200:
        y_position = add_new_page()
    c.setFont("Helvetica", 12)  # Configurar fuente normal
    c.drawString(100, y_position, f"Tipo de Muestra: {muestra.sample_type}")
    c.drawString(100, y_position - 20, f"Descripción: {muestra.sample_description}")
    c.drawString(100, y_position - 40, f"Volumen/Masa de Muestra Procesada: {muestra.sample_volume_mass}")
    c.drawString(100, y_position - 60, f"Procedimiento de Muestreo: {muestra.sampling_procedure}")
    c.drawString(100, y_position - 80, f"Método de Congelación: {muestra.freezing_method}")
    c.drawString(100, y_position - 100, f"Método de Fijación: {muestra.fixation_method}")
    c.drawString(100, y_position - 120, f"Condiciones de Almacenamiento: {muestra.storage_conditions}")
    y_position -= 140  # Bajar la posición después de cada conjunto de datos de muestra
    y_position -= 20  # Espacio vertical adicional entre cada conjunto de datos de muestra


    # Espacio vertical adicional antes de la sección de Extracción de Ácidos Nucleicos
    if y_position < 200:
        y_position = add_new_page()
    else:
        y_position -= 25  # Ajuste para agregar espacio entre secciones

    # Agregar módulo de extracción de ácidos nucleicos
    extraction_module_title = "Extracción de Ácidos Nucleicos"
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, y_position, extraction_module_title)
    y_position -= 20  # Bajar la posición después del título

    for extraction_data in datos_extraction:
     if y_position < 200:
        y_position = add_new_page()
    c.setFont("Helvetica", 12)  # Configurar fuente normal
    c.drawString(100, y_position - 20, f"Procedimiento de Extracción: {extraction_data.extraction_procedure}")
    c.drawString(100, y_position - 40, f"Detalles del Kit: {extraction_data.kit_details}")
    c.drawString(100, y_position - 60, f"Reactivos Adicionales: {extraction_data.additional_reagents}")
    c.drawString(100, y_position - 80, f"Tratamiento con DNAsa o RNAsa: {extraction_data.dnase_rnase_treatment}")
    c.drawString(100, y_position - 100, f"Evaluación de Contaminación: {extraction_data.contamination_evaluation}")
    c.drawString(100, y_position - 120, f"Método de Cuantificación de Ácidos Nucleicos: {extraction_data.nucleic_acid_quantification_method}")
    c.drawString(100, y_position - 140, f"Pureza de Ácidos Nucleicos (A260/A280): {extraction_data.nucleic_acid_purity}")
    c.drawString(100, y_position - 160, f"RIN/RQI o Cq de Transcripciones 3' y 5': {extraction_data.rin_rqi_cq_details}")
    c.drawString(100, y_position - 180, f"Método de Evaluación de la Integridad (ARN): {extraction_data.integrity_assessment_method}")
    c.drawString(100, y_position - 200, f"Rastros de Electroforesis: {extraction_data.electrophoresis_traces}")
    c.drawString(100, y_position - 220, f"Prueba de Inhibición: {extraction_data.inhibition_testing}")
    y_position -= 240  # Bajar la posición después de cada conjunto de datos de extracción
    y_position -= 20  # Espacio vertical adicional entre cada conjunto de datos de extracción


    # Espacio vertical adicional antes de la sección de Reverse Transcription
    if y_position < 200:
        y_position = add_new_page()
    else:
        y_position -= 25  # Ajuste para agregar espacio entre secciones

   # Agregar módulo de Transcripción Inversa
    reverse_transcription_module_title = "Transcripción Inversa"
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, y_position, reverse_transcription_module_title)
    y_position -= 20  # Bajar la posición después del título

    for rt_data in datos_reverse_transcription:
        if y_position < 200:
            y_position = add_new_page()
        c.setFont("Helvetica", 12)  # Configurar fuente normal
        c.drawString(100, y_position - 20, f"Condiciones de Reacción: {rt_data.reaction_conditions}")
        c.drawString(100, y_position - 40, f"Cantidad de ARN: {rt_data.rna_quantity}")
        c.drawString(100, y_position - 60, f"Volúmenes de Reacción: {rt_data.reaction_volumes}")
        c.drawString(100, y_position - 80, f"Oligonucleótidos de Iniciación: {rt_data.reverse_transcriptase_oligo_priming}")
        c.drawString(100, y_position - 100, f"Concentración de Oligo de Transcripción Inversa: {rt_data.reverse_transcriptase_oligo_concentration}")
        c.drawString(100, y_position - 120, f"Tipo de Transcripción Inversa: {rt_data.reverse_transcriptase_type}")
        c.drawString(100, y_position - 140, f"Concentración de la Transcripción Inversa: {rt_data.reverse_transcriptase_concentration}")
        c.drawString(100, y_position - 160, f"Temperatura de Transcripción Inversa: {rt_data.reverse_transcriptase_temperature}")
        c.drawString(100, y_position - 180, f"Tiempo de Reacción de Transcripción Inversa: {rt_data.reverse_transcriptase_reaction_time}")
        c.drawString(100, y_position - 200, f"Fabricante de la Transcripción Inversa: {rt_data.reverse_transcriptase_manufacturer}")
        c.drawString(100, y_position - 220, f"Número de Catálogo de la Transcripción Inversa: {rt_data.reverse_transcriptase_catalog_number}")
        c.drawString(100, y_position - 240, f"Condiciones de Almacenamiento del cDNA: {rt_data.cdna_storage_conditions}")
        y_position -= 260  # Bajar la posición después de cada conjunto de datos de Reverse Transcription
        y_position -= 20  # Espacio vertical adicional entre cada conjunto de datos de Reverse Transcription

    # Espacio vertical adicional antes de la sección de Información del Blanco de qPCR
    if y_position < 200:
        y_position = add_new_page()
    else:
        y_position -= 25  # Ajuste para agregar espacio entre secciones

    # Agregar módulo de Información del Blanco de qPCR
    qpcr_target_module_title = "Información del Blanco de qPCR"
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, y_position, qpcr_target_module_title)
    y_position -= 20  # Bajar la posición después del título

    for qpcr_data in datos_qpcr_target:
        if y_position < 200:
         y_position = add_new_page()
        c.setFont("Helvetica", 12)  # Configurar fuente normal
        c.drawString(100, y_position - 20, f"Símbolo del Gen: {qpcr_data.gene_symbol}")
        c.drawString(100, y_position - 40, f"Efficiencia Multiplex y LOD para cada Ensayo: {qpcr_data.multiplex_efficiency_lod}")
        c.drawString(100, y_position - 60, f"Número de Acceso a la Secuencia: {qpcr_data.sequence_accession_number}")
        c.drawString(100, y_position - 80, f"Localización del Amplicón: {qpcr_data.amplicon_location}")
        c.drawString(100, y_position - 100, f"Longitud del Amplicón: {qpcr_data.amplicon_length}")
        c.drawString(100, y_position - 120, f"Cribado de Especificidad In Silico: {qpcr_data.in_silico_specificity_screening}")
        c.drawString(100, y_position - 140, f"Pseudogenes, Retrogenes u Otros Homólogos: {qpcr_data.pseudogenes_homologs}")
        c.drawString(100, y_position - 160, f"Alineamiento de Secuencia: {qpcr_data.sequence_alignment}")
        c.drawString(100, y_position - 180, f"Análisis de Estructura Secundaria del Amplicón: {qpcr_data.amplicon_secondary_structure_analysis}")
        c.drawString(100, y_position - 200, f"Localización del Oligonucleótido por Exón o Intrón: {qpcr_data.primer_location_exon_intron}")
        c.drawString(100, y_position - 220, f"Variantes de Empalme Dirigidas: {qpcr_data.splicing_variants_targeted}")
        y_position -= 240  # Bajar la posición después de cada conjunto de datos de Información del Blanco de qPCR
        y_position -= 20  # Espacio vertical adicional entre cada conjunto de datos de Información del Blanco de qPCR


     # Espacio vertical adicional antes de la sección 
    if y_position < 200:
     y_position = add_new_page()
    else:
     y_position -= 25  # Ajuste para agregar espacio entre secciones

     # Agregar módulo de qPCR Primers
    qpcr_primers_module_title = "qPCR Primers"
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, y_position, qpcr_primers_module_title)
    y_position -= 20  # Bajar la posición después del título

    for primer_data in datos_qpcr_primers:
     if y_position < 200:
        y_position = add_new_page()
        c.setFont("Helvetica", 12)  # Configurar fuente normal
        c.drawString(100, y_position - 20, f"Secuencia forward: {primer_data.forward_sequence}")
        c.drawString(100, y_position - 40, f"Secuencia Reverse: {primer_data.reverse_sequence}")
        c.drawString(100, y_position - 60, f"Número de Identificación de RTPrimerDB: {primer_data.rtprimerdb_id}")
        c.drawString(100, y_position - 80, f"Secuencias de la Sonda: {primer_data.probe_sequences}")
        c.drawString(100, y_position - 100, f"Ubicación e Identidad de la Modificación: {primer_data.modification_location_identity}")
        c.drawString(100, y_position - 120, f"Fabricante del Oligo: {primer_data.oligo_manufacturer}")
        c.drawString(100, y_position - 140, f"Método de Purificación: {primer_data.purification_method}")
        y_position -= 160  # Bajar la posición después de cada conjunto de datos de qPCR Primers
        y_position -= 20  # Espacio vertical adicional entre cada conjunto de datos de qPCR Primers


    # Espacio vertical adicional antes de la sección de qPCR Protocol
    if y_position < 200:
     y_position = add_new_page()
    else:
     y_position -= 25  # Ajuste para agregar espacio entre secciones

    # Agregar módulo de qPCR Protocol
    qpcr_protocol_module_title = "Protocolo de qPCR"
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, y_position, qpcr_protocol_module_title)
    y_position -= 20  # Bajar la posición después del título

    for protocol_data in datos_qpcr_protocol:
     if y_position < 200:
        y_position = add_new_page()
        c.setFont("Helvetica", 12)  # Configurar fuente normal
        c.drawString(100, y_position - 20, f"Condiciones de Reacción: {protocol_data.reaction_conditions}")
        c.drawString(100, y_position - 40, f"Volumen de Reacción y Cantidad de ADN: {protocol_data.reaction_volume_dna_quantity}")
        c.drawString(100, y_position - 60, f"Concentraciones de Primer, Sonda, Mg++ y Dntp: {protocol_data.primer_probe_concentrations}")
        c.drawString(100, y_position - 80, f"Identidad y Concentración de la Polimerasa: {protocol_data.polymerase_identity_concentration}")
        c.drawString(100, y_position - 100, f"Identidad y Fabricante del Buffer/Kit: {protocol_data.buffer_kit_identity_manufacturer}")
        c.drawString(100, y_position - 120, f"Constitución Química Exacta del Buffer: {protocol_data.buffer_exact_chemical_constitution}")
        c.drawString(100, y_position - 140, f"Aditivos: {protocol_data.additives}")
        c.drawString(100, y_position - 160, f"Fabricante y Número de Catálogo de Placas/Tubos: {protocol_data.plates_tubes_manufacturer_catalog}")
        c.drawString(100, y_position - 180, f"Parámetros de Termociclado: {protocol_data.thermocycling_parameters}")
        c.drawString(100, y_position - 200, f"Configuración de la Reacción: {protocol_data.reaction_configuration}")
        c.drawString(100, y_position - 220, f"Fabricante del Instrumento de qPCR: {protocol_data.qpcr_instrument_manufacturer}")
        c.drawString(100, y_position - 240, f"Control de Calidad de la Reacción: {protocol_data.reaction_quality_control}")
        y_position -= 260  # Bajar la posición después de cada conjunto de datos de qPCR Protocol
        y_position -= 20  # Espacio vertical adicional entre cada conjunto de datos de qPCR Protocol


    # Espacio vertical adicional antes de la sección de Análisis de Datos
    if y_position < 200:
      y_position = add_new_page()
    else:
     y_position -= 25  # Ajuste para agregar espacio entre secciones

    # Agregar módulo de Análisis de Datos
    data_analysis_module_title = "Análisis de Datos"
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, y_position, data_analysis_module_title)
    y_position -= 20  # Bajar la posición después del título

    for analysis_data in datos_data_analysis:
     if y_position < 200:
        y_position = add_new_page()
        c.setFont("Helvetica", 12)  # Configurar fuente normal
        c.drawString(100, y_position - 20, f"Programa de Análisis de qPCR: {analysis_data.qpcr_analysis_program}")
        c.drawString(100, y_position - 40, f"Método de Determinación de Cq: {analysis_data.cq_method_determination}")
        c.drawString(100, y_position - 60, f"Identificación y Manejo de Valores Atípicos: {analysis_data.identification_handling_outliers}")
        c.drawString(100, y_position - 80, f"Resultados de NTC: {analysis_data.ntc_results}")
        c.drawString(100, y_position - 100, f"Justificación del Número y Elección de Genes de Referencia: {analysis_data.reference_genes_justification}")
        c.drawString(100, y_position - 120, f"Descripción del Método de Normalización: {analysis_data.normalization_method_description}")
        c.drawString(100, y_position - 140, f"Número y Concordancia de Réplicas Biológicas: {analysis_data.biological_replicates_number_concordance}")
        c.drawString(100, y_position - 160, f"Número y Etapa de Réplicas Técnicas: {analysis_data.technical_replicates_number_stage}")
        c.drawString(100, y_position - 180, f"Repetibilidad (Variación Intra-Ensayo): {analysis_data.intra_assay_variation_repeatability}")
        c.drawString(100, y_position - 200, f"Reproducibilidad (Variación Inter-Ensayo, %CV): {analysis_data.inter_assay_variation_reproducibility}")
        c.drawString(100, y_position - 220, f"Análisis de Potencia: {analysis_data.power_analysis}")
        c.drawString(100, y_position - 240, f"Métodos Estadísticos para Significancia de Resultados: {analysis_data.statistical_methods_significance}")
        c.drawString(100, y_position - 260, f"Software (fuente, versión): {analysis_data.software_source_version}")
        c.drawString(100, y_position - 280, f"Cq o Envío de Datos Crudos utilizando RDML: {analysis_data.cq_or_raw_data_rdml_submission}")
        y_position -= 300  # Bajar la posición después de cada conjunto de datos de Análisis de Datos
        y_position -= 20  # Espacio vertical adicional entre cada conjunto de datos de Análisis de Datos


    # Espacio vertical adicional antes de la sección 
    if y_position < 200:
     y_position = add_new_page()
    else:
     y_position -= 100  # Ajuste para agregar espacio entre secciones


    # Agregar módulo de Thermal Cycling Conditions
    thermal_cycling_module_title = "Condiciones de Ciclado Térmico"
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, y_position, thermal_cycling_module_title)
    y_position -= 20  # Bajar la posición después del título

    for tc_data in datos_thermal_cycling_conditions:
     if y_position < 200:
        y_position = add_new_page()
        c.setFont("Helvetica", 12)  # Configurar fuente normal
        c.drawString(100, y_position - 20, f"Equipo Utilizado: {tc_data.equipment_used}")
        c.drawString(100, y_position - 40, f"Pruebas Utilizadas: {tc_data.primers_used}")
        c.drawString(100, y_position - 60, f"Condiciones de PCR: {tc_data.pcr_conditions}")
        c.drawString(100, y_position - 80, f"Volumen de Reacción: {tc_data.reaction_volume}")
        c.drawString(100, y_position - 100, f"Control Positivo: {tc_data.positive_control}")
        c.drawString(100, y_position - 120, f"Control Negativo: {tc_data.negative_control}")
        y_position -= 140  # Descender la posición después de cada conjunto de datos de Condiciones de Ciclado Térmico
        y_position -= 20  # Espacio vertical adicional entre cada conjunto de datos de Condiciones de Ciclado Térmico
 
    # Espacio vertical adicional antes de la sección
    if y_position < 200:
     y_position = add_new_page()
    else:
     y_position -= 100  # Ajuste para agregar espacio entre secciones

    # Agregar módulo de Validación de qPCR
    titulo_modulo_validacion_qpcr = "Validación de qPCR"
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, y_position, titulo_modulo_validacion_qpcr)
    y_position -= 20  # Bajar la posición después del título

    for datos_validacion_qpcr in datos_qpcr_validation:
     if y_position < 200:
        y_position = add_new_page()
        c.setFont("Helvetica", 12)  # Configurar fuente normal
        c.drawString(100, y_position - 20, f"Evidencia de Optimización: {datos_validacion_qpcr.optimization_evidence}")
        c.drawString(100, y_position - 40, f"Evidencia de Especificidad: {datos_validacion_qpcr.specificity_evidence}")
        c.drawString(100, y_position - 60, f"Cq del NTC para SYBR Green I: {datos_validacion_qpcr.cq_nct_for_sybr_green}")
        c.drawString(100, y_position - 80, f"Curvas Estándar con Pendiente e Intercepto: {datos_validacion_qpcr.standard_curves_slope_intercept}")
        c.drawString(100, y_position - 100, f"Eficiencia de PCR Calculada a partir de la Pendiente: {datos_validacion_qpcr.pcr_efficiency_slope_calculation}")
        c.drawString(100, y_position - 120, f"Intervalo de Confianza para la Eficiencia de PCR: {datos_validacion_qpcr.pcr_efficiency_confidence_interval}")
        c.drawString(100, y_position - 140, f"R^2 de la Curva Estándar: {datos_validacion_qpcr.r2_standard_curve}")
        c.drawString(100, y_position - 160, f"Rango Dinámico Lineal: {datos_validacion_qpcr.linear_dynamic_range}")
        c.drawString(100, y_position - 180, f"Variación de Cq en el Límite Inferior: {datos_validacion_qpcr.cq_variation_lower_limit}")
        c.drawString(100, y_position - 200, f"Intervalos de Confianza a lo largo de Todo el Rango: {datos_validacion_qpcr.confidence_intervals_full_range}")
        c.drawString(100, y_position - 220, f"Evidencia de Límite de Detección: {datos_validacion_qpcr.lod_evidence}")
        c.drawString(100, y_position - 240, f"Si es Multiplex, Eficiencia y LOD para Cada Ensayo: {datos_validacion_qpcr.multiplex_efficiency_lod}")
        y_position -= 260  # Descender la posición después de cada conjunto de datos de Validación de qPCR
        y_position -= 20  # Espacio vertical adicional entre cada conjunto de datos de Validación de qPCR


    # Espacio vertical adicional antes de la sección
    if y_position < 200:
     y_position = add_new_page()
    else:
     y_position -= 100  # Ajuste para agregar espacio entre secciones

    # Agregar módulo de Datos de PCR en Tiempo Real
    titulo_modulo_pcr_tiempo_real = "Datos de PCR en Tiempo Real"
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, y_position, titulo_modulo_pcr_tiempo_real)
    y_position -= 20  # Bajar la posición después del título

    for datos_pcr_tiempo_real in datos_realtime_pcr_data:
     if y_position < 200:
        y_position = add_new_page()
        c.setFont("Helvetica", 12)  # Configurar fuente normal
        c.drawString(100, y_position - 20, f"Software de Análisis de Datos: {datos_pcr_tiempo_real.data_analysis_software}")
        c.drawString(100, y_position - 40, f"Método de Cuantificación: {datos_pcr_tiempo_real.quantification_method}")
        c.drawString(100, y_position - 60, f"Datos Crudos: {datos_pcr_tiempo_real.raw_data}")
        y_position -= 80  # Descender la posición después de cada conjunto de datos de PCR en Tiempo Real
        y_position -= 20  # Espacio vertical adicional entre cada conjunto de datos de PCR en Tiempo Real


    # Espacio vertical adicional antes de la sección
    if y_position < 200:
     y_position = add_new_page()
    else:
     y_position -= 100  # Ajuste para agregar espacio entre secciones

    # Agregar módulo de Resultados y Análisis
    titulo_modulo_resultados_analisis = "Resultados y Análisis"
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, y_position, titulo_modulo_resultados_analisis)
    y_position -= 20  # Bajar la posición después del título

    for datos_resultados_analisis in datos_results_analysis:
     if y_position < 200:
        y_position = add_new_page()
        c.setFont("Helvetica", 12)  # Configurar fuente normal
        c.drawString(100, y_position - 20, f"Interpretación de Resultados: {datos_resultados_analisis.results_interpretation}")
        c.drawString(100, y_position - 40, f"Gráficos y Figuras: {datos_resultados_analisis.charts_figures}")
        y_position -= 60  # Descender la posición después de cada conjunto de datos de Resultados y Análisis
        y_position -= 20  # Espacio vertical adicional entre cada conjunto de datos de Resultados y Análisis


    c.save()

    # Devolver el PDF como respuesta
    buffer.seek(0)
    response = make_response(buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=informe_experimento.pdf'
    return response


if __name__ == '__main__':
    app.run(debug=True)
