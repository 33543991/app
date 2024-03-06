from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SubmitField, DateField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo
from flask_bcrypt import Bcrypt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
from uuid import uuid4 
from Bio import Entrez
from io import BytesIO



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
    nombre = StringField('Nombre', validators=[DataRequired()])
    apellido_paterno = StringField('Apellido Paterno', validators=[DataRequired()])
    apellido_materno = StringField('Apellido Materno', validators=[DataRequired()])
    telefono = StringField('Teléfono', validators=[DataRequired()])
    correo = StringField('Correo', validators=[DataRequired(), Email()])
    laboratorio = StringField('Laboratorio', validators=[DataRequired()])
    institucion = StringField('Institución', validators=[DataRequired()])
    contrasena = PasswordField('Contraseña', validators=[DataRequired()])
    verificacion_contrasena = PasswordField('Verificación de Contraseña', validators=[DataRequired(), EqualTo('contrasena')])
    submit = SubmitField('Agregar Registro')

# General Information
class GeneralInfoForm(FlaskForm):
    experiment_date = StringField('Fecha del experimento', validators=[DataRequired()])
    experiment_number = StringField('Número de experimento', validators=[DataRequired()])
    principal_investigator = StringField('Principal Investigator', validators=[DataRequired()])
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
    sample_type_choices = [('DNA', 'ADN Genómico'), ('RNA', 'ARN Total'), ('Plasmids', 'Plasmidos'), ('Culture', 'Cultivos celulares'), ('Tissue', 'Tejidos'), ('Blood', 'Sangre'), ('Fluids', 'Fuidos biologicos'), ('Vegetal', 'Tejidos vegetales'), ('Environment', 'Muestras ambientales'), ('FTA', 'Tarjetas FTA')]
    sampling_procedure_choices = [('Micro', 'Microdisección'), ('Hisope', 'Hisopado'), ('Micropunction', 'Micropunción'), ('Dilute', 'Dilución seriada')]
    freezing_method_choices = [('Cooler4','Refrigeración 4°C'), ('Cooler8','Refrigeración 8°C'), ('Freezing','Congelación -20°C'), ('UltraFreezing','Ultracongelacion -70°C'), ('CarbonDioxide','Hielo Seco -78.5°C'), ('LiquidNitrogen','Nitrogeno Líquido -196°C')]
    sample_volume_mass_choices = [('MicroVolume','<200 uL'),('MacroVolume','>200 uL'),('Microsample','<200 ug'), ('MacroSample','>200 ug')]
    fixation_method_sample_choices = [('None','Ninguna'),('Formol','Formol'),('FFPE','Tejido Embebido en Parafina'), ('CytoSpray','Cytospray')]
    storage_conditions_choices = [('Cooler4','Refrigeración 4°C'), ('Cooler8','Refrigeración 8°C'), ('Freezing','Congelación -20°C'), ('UltraFreezing','Ultracongelacion -70°C'), ('CarbonDioxide','Hielo Seco -78.5°C'), ('LiquidNitrogen','Nitrogeno Líquido -196°C')]


    sample_type = SelectField('Sample Type', choices=sample_type_choices, validators=[DataRequired()], default='DNA')
    sample_description = TextAreaField('Description', validators=[DataRequired()])
    sample_volume_mass = SelectField('Volume/Mass of Processed Sample', choices=sample_volume_mass_choices, validators=[DataRequired()], default="MicroVolumen")
    sampling_procedure = SelectField('Sampling Procedure', choices=sampling_procedure_choices, validators=[DataRequired()], default='Micro')
    freezing_method = SelectField('Freezing Method', choices=freezing_method_choices, validators=[DataRequired()], default = "Cooler4")
    fixation_method = SelectField('Fixation Method', choices=fixation_method_sample_choices, validators=[DataRequired()], default='None')
    storage_conditions = SelectField('Storage Conditions and Duration', choices=storage_conditions_choices, validators=[DataRequired()], default='Cooler4')
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
    # Procedimiento de extracción
    extraction_procedure_choices = [
        ('organic', 'Fenol/cloroformo/alcohol isoamílico (25:24:1)'),
        ('trizol', 'Trizol'),
        ('resin', 'Resina'),
        ('column', 'Columnas'),
        ('robot', 'Automática/Robóticas'),
        ('magnetic', 'Magnética')
    ]

    # Detalles del kit
    kit_details_choices = [
        ('DNA', 'ADN'),
        ('RNA', 'ARN'),
        ('DNA/RNA', 'ADN/ARN'),
        ('plasmid', 'Plásmido'),
        ('agarose', 'Remoción de agarosa'),
        ('paraffin', 'Remoción de parafina')
    ]

    # Reactivos adicionales
    additional_reagents_choices = [
        ('None', 'Ninguno'),
        ('custom', 'Optimizado en laboratorio')
    ]

    # Tratamiento con DNAsa o RNAsa
    dnase_rnase_treatment_choices = [
        ('None', 'Ninguno'),
        ('dnase', 'Tratamiento con DNAsa'),
        ('rnase', 'Tratamiento con RNAsa')
    ]

    # Evaluación de contaminación
    contamination_evaluation_choices = [
        ('complete', 'C+, C-, NTC'),
        ('partial', 'C+, C-'),
        ('None', 'Ninguno')
    ]

    # Métodos de cuantificación de ácidos nucleicos
    nucleic_acid_quantification_method_choices = [
        ('uv', 'Espectroscopía Ultravioleta UV'),
        ('fluorescent', 'Espectroscopía de Fluorescencia'),
        ('nanodrop', 'Cuantificación en Nanodrop'),
        ('gel', 'Cuantificación mediante gel de referencia'),
        ('plasmid', 'Plásmido de referencia'),
        ('qpcr', 'PCR cuantitativo'),
        ('digitalpcr', 'PCR digital')
    ]

    nucleic_acid_purity_choices = [
        ('good','1.7-2.0'),
        ('low','<1.7'),
        ('high','>2.0'),
        ('None','Dato no disponible'),
    ]

    nucleic_acid_yield_choices = [
        ('None','Sin Datos'),
        ('data','Inserte dato'),
    ]

    integrity_assessment_method_choices = [
        ('spectrometric', 'Medidas espectrométricas'),
        ('electrophoresis', 'Electroforesis en gel'),
        ('capillary', 'Electroforesis capilar'),
        ('microfluids', 'Microfluidos')
    ]

    electrophoresis_traces_choices = [
        ('zero','No se observa degradación'),
        ('low','Baja degradación'),
        ('high','Alta degradación'),
        ('None','Degradación no comprobada'),
    ]

    inhibition_testing_choices = [
        ('None', 'Ninguno'),
        ('SPUD', 'Prueba SPUD'),
        ('endogenous', 'Control Endógeno')
    ]

    extraction_procedure = SelectField('Extraction Procedure and/or Instrumentation', 
                                       choices=extraction_procedure_choices,
                                       validators=[DataRequired()],
                                       default='organic')

    kit_details = SelectField('Kit Details and Any Modifications', 
                              choices=kit_details_choices,
                              validators=[DataRequired()],
                              default='DNA')

    additional_reagents = SelectField('Source of Additional Reagents Used', 
                                      choices=additional_reagents_choices,
                                      validators=[DataRequired()],
                                      default='None')

    dnase_rnase_treatment = SelectField('Details of DNase or RNase Treatment', 
                                         choices=dnase_rnase_treatment_choices,
                                         validators=[DataRequired()], 
                                         default='None')

    contamination_evaluation = SelectField('Contamination Evaluation (DNA or RNA)', 
                                           choices=contamination_evaluation_choices,
                                           validators=[DataRequired()],
                                           default='complete')

    nucleic_acid_quantification_method = SelectField('Nucleic Acid Quantification Method (Instrument and Method)', 
                                                     choices=nucleic_acid_quantification_method_choices,
                                                     validators=[DataRequired()],
                                                     default='uv')

    
    nucleic_acid_purity = SelectField('Nucleic Acid Purity (A260/A280)', 
                                      choices=nucleic_acid_purity_choices,
                                      validators=[DataRequired()],
                                      default='None')


    nucleic_acid_yield = SelectField('Nucleic Acid Yield', 
                                     choices=nucleic_acid_yield_choices,
                                     validators=[DataRequired()],
                                     default='None')

    rin_rqi_cq_details = StringField("RIN/RQI or Cq of 3' and 5' Transcriptions", validators=[DataRequired()])
    
    
    integrity_assessment_method = SelectField('Integrity Assessment Method (RNA)', 
                                              choices=integrity_assessment_method_choices,
                                              validators=[DataRequired()],
                                              default='spectrometric')


    electrophoresis_traces = SelectField('Electrophoresis Traces', 
                                         choices=electrophoresis_traces_choices,
                                         validators=[DataRequired()],
                                         default='zero')

    inhibition_testing = SelectField('Inhibition Testing (Cq dilutions, peaks, or others)', 
                                     choices=inhibition_testing_choices,
                                     validators=[DataRequired()],
                                     default='endogenous')
    
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

    # E - Complete reaction conditions
    reaction_conditions = SelectField(
        label='Reaction Conditions',
        choices=[
            ('one', 'One Step protocol'),
            ('two', 'Two Step protocol')
        ],
        validators=[DataRequired()],
        default='one'
    )

    # E - Amount of RNA and reaction volumes
    rna_quantity = StringField(
        label='RNA Quantity',
        validators=[DataRequired()]
    )

    reaction_volumes = StringField(
        label='Reaction Volumes',
        validators=[DataRequired()]
    )

    # E - Priming oligonucleotides (if using GSP) and concentration
    reverse_transcriptase_oligo_priming = SelectField(
        label='Priming Oligonucleotides',
        choices=[
            ('dT18', 'Oligo dT18'),
            ('RHP', 'Random Hexamer Primers (RHP)'),
            ('GSP', 'Gen Specific Priming (GSP)'),
            ('Mix', 'Mix Oligo dT18 and Random Hexamer Primers (dT18/RHP)')
        ],
        validators=[DataRequired()],
        default='Mix'
    )

    reverse_transcriptase_oligo_concentration = StringField(
        label='Reverse Transcriptase Oligo Concentration',
        validators=[DataRequired()]
    )

    # E - Reverse transcriptase and concentration
    reverse_transcriptase_type = SelectField(
        label='Reverse Transcriptase Type',
        choices=[
            ('AMV', 'Avian Myoblastosis Virus (AMV)'),
            ('M-MLV', 'Maloney Murine Leukemia Virus (M-MLV)')
        ],
        validators=[DataRequired()],
        default='AMV'
    )

    reverse_transcriptase_concentration = StringField(
        label='Reverse Transcriptase Concentration',
        validators=[DataRequired()]
    )

    # E - Temperature and time
    reverse_transcriptase_temperature = StringField(
        label='Reverse Transcriptase Temperature',
        validators=[DataRequired()]
    )

    reverse_transcriptase_reaction_time = StringField(
        label='Reverse Transcriptase Reaction Time',
        validators=[DataRequired()]
    )

    # D - Manufacturer of reagents and catalog numbers
    reverse_transcriptase_manufacturer = StringField(
        label='Reverse Transcriptase Manufacturer',
        validators=[DataRequired()]
    )

    reverse_transcriptase_catalog_number = StringField(
        label='Reverse Transcriptase Catalog Number',
        validators=[DataRequired()]
    )

    # D - Cqs with and without reverse transcription
    # This parameter was omitted

    # D - Storage conditions of cDNA
    cdna_storage_conditions = SelectField(
        label='cDNA Storage Conditions',
        choices=[
            ('none', 'Fresh cDNA Sample'),
            ('overnight', 'Overnight 4°C'),
            ('freezer', 'Freezer -20°C'),
            ('ultrafreezer', 'Ultrafreezer -80°C')
        ],
        validators=[DataRequired()],
        default='none'
    )

    # Submit
    Submit = SubmitField('Submit')

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


# qPCR Target Information
class qPCRTargetInfoForm(FlaskForm):
    gene_symbol = StringField('Gene Symbol', validators=[DataRequired()])
    multiplex_efficiency_lod = StringField('Multiplex Efficiency and LOD for Each Assay', validators=[DataRequired()])
    sequence_accession_number = StringField('Sequence Accession Number', validators=[DataRequired()])
    amplicon_location = StringField('Amplicon Location', validators=[DataRequired()])
    amplicon_length = StringField('Amplicon Length', validators=[DataRequired()])
    in_silico_specificity_screening = StringField('In Silico Specificity Screening (BLAST, etc.)', validators=[DataRequired()])
    pseudogenes_homologs = StringField('Pseudogenes, Retropseudogenes, or Other Homologs', validators=[DataRequired()])
    sequence_alignment = StringField('Sequence Alignment', validators=[DataRequired()])
    amplicon_secondary_structure_analysis = StringField('Amplicon Secondary Structure Analysis', validators=[DataRequired()])
    primer_location_exon_intron = StringField('Primer Location by Exon or Intron (if applicable)', validators=[DataRequired()])
    splicing_variants_targeted = StringField('Splicing Variants Targeted', validators=[DataRequired()])
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

# qPCR Primers
class qPCRPrimersForm(FlaskForm):
    forward_sequence = StringField('Forward sequence', validators=[DataRequired()])
    reverse_sequence = StringField('Reverse sequence', validators=[DataRequired()])
    rtprimerdb_id = StringField('RTPrimerDB Identification Number', validators=[DataRequired()])
    probe_sequences = StringField('Probe Sequences (if applicable)')
    modification_location_identity = StringField('Modification Location and Identity', validators=[DataRequired()])
    oligo_manufacturer = StringField('Oligo Manufacturer', validators=[DataRequired()])
    purification_method = StringField('Purification Method', validators=[DataRequired()])
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
class qPCRProtocolForm(FlaskForm):
    reaction_conditions = StringField('Reaction Conditions', validators=[DataRequired()])
    reaction_volume_dna_quantity = StringField('Reaction Volume and DNA Quantity', validators=[DataRequired()])
    primer_probe_concentrations = StringField('Primer, Probe, Mg++, and Dntp Concentrations', validators=[DataRequired()])
    polymerase_identity_concentration = StringField('Polymerase Identity and Concentration', validators=[DataRequired()])
    buffer_kit_identity_manufacturer = StringField('Buffer/Kit Identity and Manufacturer', validators=[DataRequired()])
    buffer_exact_chemical_constitution = StringField('Exact Chemical Constitution of the Buffer', validators=[DataRequired()])
    additives = StringField('Additives (SYBR Green I, DMSO, etc.)', validators=[DataRequired()])
    plates_tubes_manufacturer_catalog = StringField('Plates/Tubes Manufacturer and Catalog Number', validators=[DataRequired()])
    thermocycling_parameters = StringField('Thermocycling Parameters', validators=[DataRequired()])
    reaction_configuration = StringField('Reaction Configuration (manual/automatic)', validators=[DataRequired()])
    qpcr_instrument_manufacturer = StringField('qPCR Instrument Manufacturer', validators=[DataRequired()])
    reaction_quality_control = StringField('Reaction Quality Control', validators=[DataRequired()])
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
    qpcr_analysis_program = StringField('qPCR Analysis Program (source, version)', validators=[DataRequired()])
    cq_method_determination = StringField('Cq Method Determination', validators=[DataRequired()])
    identification_handling_outliers = StringField('Identification and Handling of Outliers', validators=[DataRequired()])
    ntc_results = StringField('NTC Results', validators=[DataRequired()])
    reference_genes_justification = StringField('Justification of Number and Choice of Reference Genes', validators=[DataRequired()])
    normalization_method_description = StringField('Normalization Method Description', validators=[DataRequired()])
    biological_replicates_number_concordance = StringField('Number and Concordance of Biological Replicates', validators=[DataRequired()])
    technical_replicates_number_stage = StringField('Number and Stage (RT or qPCR) of Technical Replicates', validators=[DataRequired()])
    intra_assay_variation_repeatability = StringField('Repeatability (Intra-Assay Variation)', validators=[DataRequired()])
    inter_assay_variation_reproducibility = StringField('Reproducibility (Inter-Assay Variation, %CV)', validators=[DataRequired()])
    power_analysis = StringField('Power Analysis', validators=[DataRequired()])
    statistical_methods_significance = StringField('Statistical Methods for Significance of Results', validators=[DataRequired()])
    software_source_version = StringField('Software (source, version)', validators=[DataRequired()])
    cq_or_raw_data_rdml_submission = StringField('Cq or Submission of Raw Data using RDML', validators=[DataRequired()])
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
    equipment_used = StringField('Equipment Used', validators=[DataRequired()])
    primers_used = StringField('Primers Used', validators=[DataRequired()])
    pcr_conditions = StringField('PCR Conditions: Number of Cycles/Denaturation Temperature/Annealing Temperature/Extension Temperature', validators=[DataRequired()])
    reaction_volume = StringField('Reaction Volume', validators=[DataRequired()])
    positive_control = StringField('Positive Control', validators=[DataRequired()])
    negative_control = StringField('Negative Control', validators=[DataRequired()])
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
    optimization_evidence = StringField('Optimization Evidence (from gradients)', validators=[DataRequired()])
    specificity_evidence = StringField('Specificity Evidence (gel, sequence, melt, or digest)', validators=[DataRequired()])
    cq_nct_for_sybr_green = StringField('For SYBR Green I, Cq of NCT', validators=[DataRequired()])
    standard_curves_slope_intercept = StringField('Standard Curves with Slope and Intercept', validators=[DataRequired()])
    pcr_efficiency_slope_calculation = StringField('PCR Efficiency Calculated from Slope', validators=[DataRequired()])
    pcr_efficiency_confidence_interval = StringField('Confidence Interval for PCR Efficiency', validators=[DataRequired()])
    r2_standard_curve = StringField('R^2 of the Standard Curve', validators=[DataRequired()])
    linear_dynamic_range = StringField('Linear Dynamic Range', validators=[DataRequired()])
    cq_variation_lower_limit = StringField('Cq Variation at the Lower Limit', validators=[DataRequired()])
    confidence_intervals_full_range = StringField('Confidence Intervals across the Full Range', validators=[DataRequired()])
    lod_evidence = StringField('LOD Evidence', validators=[DataRequired()])
    multiplex_efficiency_lod = StringField('If Multiplex, Efficiency and LOD for Each Assay', validators=[DataRequired()])
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
    data_analysis_software = StringField('Data Analysis Software', validators=[DataRequired()])
    quantification_method = StringField('Quantification Method', validators=[DataRequired()])
    raw_data = StringField('Raw Data: Threshold Cycle (Ct): Target Gene (name and Ct value) /Reference Gene (name and Ct value); Amplification Efficiency', validators=[DataRequired()])
    submit = SubmitField('Enviar')

class RealTimePCRDataModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_analysis_software = db.Column(db.String(255), nullable=False)
    quantification_method = db.Column(db.String(255), nullable=False)
    raw_data = db.Column(db.String(255), nullable=False)


# Results and Analysis
class ResultsAnalysisForm(FlaskForm):
    results_interpretation = StringField('Results Interpretation', validators=[DataRequired()])
    charts_figures = StringField('Charts and Figures (include amplification plots and other relevant data)', validators=[DataRequired()])
    submit = SubmitField('Enviar')

class ResultsAnalysisModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    results_interpretation = db.Column(db.String(255), nullable=False)
    charts_figures = db.Column(db.String(255), nullable=False)


# Crear las tablas dentro del contexto de la aplicación
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

# LOGIN

# Esta es la ruta de inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Aquí se verifica el inicio de sesión
        # Si el inicio de sesión es exitoso, establece la sesión del usuario
        session['username'] = request.form['username']
        # Redirige al usuario al dashboard después de iniciar sesión
        return redirect(url_for('dashboard'))
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

# ABOUT
@app.route('/about')
def about():
    return render_template('about.html')

# CONTACT
@app.route('/contact')
def contact():
    return render_template('contact.html')

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
            nombre = user.nombre
            apellido_paterno = user.apellido_paterno
            apellido_materno = user.apellido_materno
            telefono = user.telefono
            correo = user.correo
            laboratorio = user.laboratorio
            institucion = user.institucion

            return render_template('profile.html', username=username, nombre=nombre, apellido_paterno=apellido_paterno, apellido_materno=apellido_materno, telefono=telefono, correo=correo, laboratorio=laboratorio, institucion=institucion)
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
            institution_lab = f"{user.laboratorio} {user.institucion}"

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
            return redirect(url_for('index'))
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

        return redirect(url_for('index'))
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

        return redirect(url_for('index'))
    return render_template('sample.html', form=form)

# Extracción de Ácido Nucleico
@app.route('/extraction', methods=['GET', 'POST'])
def nucleic_acid_extraction():
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

        return redirect(url_for('index'))
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
        
        return redirect(url_for('index')) 
    
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

        return redirect(url_for('index'))
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

        return redirect(url_for('index'))
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

        return redirect(url_for('index'))
    return render_template('protocol.html', form=form)

# Data Analysis
@app.route('/analyze', methods=['GET', 'POST'])
def data_analysis():
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
            return redirect(url_for('index'))
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

        return redirect(url_for('index'))
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
            return redirect(url_for('index'))
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
            return redirect(url_for('index'))
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

        return redirect(url_for('index'))
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

    # Establecer posición inicial para los datos
    y_position = 750

    # Función para agregar una nueva página
    def add_new_page():
        c.showPage()
        c.setFont("Helvetica-Bold", 16)
        return 750

    # Agregar módulo de información general
    general_module_title = "Información General"
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, y_position, general_module_title)
    c.drawString(100, y_position - 20, f"Fecha del Experimento: {datos_general.experiment_date}")
    c.drawString(100, y_position - 40, f"Número del Experimento: {datos_general.experiment_number}")
    c.drawString(100, y_position - 60, f"Investigador Principal: {datos_general.principal_investigator}")
    c.drawString(100, y_position - 80, f"Institución (y Laboratorio): {datos_general.institution_lab}")

    # Espacio vertical adicional antes de la sección de Datos del Experimento
    if y_position < 200:
        y_position = add_new_page()
    else:
        y_position -= 100  # Ajuste para agregar espacio entre secciones

    # Agregar título del módulo "Datos del Experimento"
    module_title = "Datos del Experimento"
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, y_position, module_title)
    y_position -= 20  # Bajar la posición después del título

    # Agregar datos de cada experimento
    for dato in datos_experimento:
        if y_position < 200:
            y_position = add_new_page()
        c.drawString(100, y_position, f"Definición del Grupo Control: {dato.group_control_definition}")
        c.drawString(100, y_position - 20, f"Definición del Grupo Experimental: {dato.group_experimental_definition}")
        c.drawString(100, y_position - 40, f"Número de Grupo Control: {dato.group_control_number}")
        c.drawString(100, y_position - 60, f"Número de Grupo Experimental: {dato.group_experimental_number}")
        y_position -= 80  # Bajar la posición después de cada conjunto de datos del experimento
        y_position -= 20  # Espacio vertical adicional entre cada conjunto de datos del experimento

    # Espacio vertical adicional antes de la sección de Muestra
    if y_position < 200:
        y_position = add_new_page()
    else:
        y_position -= 100  # Ajuste para agregar espacio entre secciones
    
    # Agregar módulo de muestra
    sample_module_title = "Muestra"
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, y_position, sample_module_title)
    for muestra in datos_muestra:
        if y_position < 200:
            y_position = add_new_page()
        c.drawString(100, y_position - 20, f"Tipo de Muestra: {muestra.sample_type}")
        c.drawString(100, y_position - 40, f"Descripción: {muestra.sample_description}")
        c.drawString(100, y_position - 60, f"Volumen/Masa de Muestra Procesada: {muestra.sample_volume_mass}")
        c.drawString(100, y_position - 80, f"Procedimiento de Muestreo: {muestra.sampling_procedure}")
        c.drawString(100, y_position - 100, f"Método de Congelación: {muestra.freezing_method}")
        c.drawString(100, y_position - 120, f"Método de Fijación: {muestra.fixation_method}")
        c.drawString(100, y_position - 140, f"Condiciones de Almacenamiento: {muestra.storage_conditions}")
        y_position -= 160  # Bajar la posición después de cada conjunto de datos de muestra
        y_position -= 20  # Espacio vertical adicional entre cada conjunto de datos de muestra

    # Espacio vertical adicional antes de la sección de Extracción de Ácidos Nucleicos
    if y_position < 200:
        y_position = add_new_page()
    else:
        y_position -= 100  # Ajuste para agregar espacio entre secciones

    # Agregar módulo de extracción de ácidos nucleicos
    extraction_module_title = "Extracción de Ácidos Nucleicos"
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, y_position, extraction_module_title)
    for extraction_data in datos_extraction:
        if y_position < 200:
            y_position = add_new_page()
        c.drawString(100, y_position - 20, f"Procedimiento de Extracción: {extraction_data.extraction_procedure}")
        c.drawString(100, y_position - 40, f"Detalles del Kit: {extraction_data.kit_details}")
        c.drawString(100, y_position - 60, f"Reactivos Adicionales: {extraction_data.additional_reagents}")
        c.drawString(100, y_position - 80, f"Tratamiento con DNAsa o RNAsa: {extraction_data.dnase_rnase_treatment}")
        c.drawString(100, y_position - 100, f"Evaluación de Contaminación: {extraction_data.contamination_evaluation}")
        c.drawString(100, y_position - 120, f"Método de Cuantificación de Ácidos Nucleicos: {extraction_data.nucleic_acid_quantification_method}")
        c.drawString(100, y_position - 140, f"Pureza de Ácidos Nucleicos (A260/A280): {extraction_data.nucleic_acid_purity}")
        c.drawString(100, y_position - 160, f"RIN/RQI or Cq of 3' and 5' Transcriptions: {extraction_data.rin_rqi_cq_details}")
        c.drawString(100, y_position - 180, f"Método de Evaluación de la Integridad (RNA): {extraction_data.integrity_assessment_method}")
        c.drawString(100, y_position - 200, f"Rastros de Electroforesis: {extraction_data.electrophoresis_traces}")
        c.drawString(100, y_position - 220, f"Prueba de Inhibición: {extraction_data.inhibition_testing}")
        y_position -= 240  # Bajar la posición después de cada conjunto de datos de extracción
        y_position -= 20  # Espacio vertical adicional entre cada conjunto de datos de extracción

    # Espacio vertical adicional antes de la sección de Reverse Transcription
    if y_position < 200:
        y_position = add_new_page()
    else:
        y_position -= 100  # Ajuste para agregar espacio entre secciones

    # Agregar módulo de Reverse Transcription
    reverse_transcription_module_title = "Reverse Transcription"
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, y_position, reverse_transcription_module_title)
    for rt_data in datos_reverse_transcription:
        if y_position < 200:
            y_position = add_new_page()
        c.drawString(100, y_position - 20, f"Reaction Conditions: {rt_data.reaction_conditions}")
        c.drawString(100, y_position - 40, f"RNA Quantity: {rt_data.rna_quantity}")
        c.drawString(100, y_position - 60, f"Reaction Volumes: {rt_data.reaction_volumes}")
        c.drawString(100, y_position - 80, f"Priming Oligonucleotides: {rt_data.reverse_transcriptase_oligo_priming}")
        c.drawString(100, y_position - 100, f"Reverse Transcriptase Oligo Concentration: {rt_data.reverse_transcriptase_oligo_concentration}")
        c.drawString(100, y_position - 120, f"Reverse Transcriptase Type: {rt_data.reverse_transcriptase_type}")
        c.drawString(100, y_position - 140, f"Reverse Transcriptase Concentration: {rt_data.reverse_transcriptase_concentration}")
        c.drawString(100, y_position - 160, f"Reverse Transcriptase Temperature: {rt_data.reverse_transcriptase_temperature}")
        c.drawString(100, y_position - 180, f"Reverse Transcriptase Reaction Time: {rt_data.reverse_transcriptase_reaction_time}")
        c.drawString(100, y_position - 200, f"Reverse Transcriptase Manufacturer: {rt_data.reverse_transcriptase_manufacturer}")
        c.drawString(100, y_position - 220, f"Reverse Transcriptase Catalog Number: {rt_data.reverse_transcriptase_catalog_number}")
        c.drawString(100, y_position - 240, f"cDNA Storage Conditions: {rt_data.cdna_storage_conditions}")
        y_position -= 260  # Bajar la posición después de cada conjunto de datos de Reverse Transcription
        y_position -= 20  # Espacio vertical adicional entre cada conjunto de datos de Reverse Transcription

        # Espacio vertical adicional antes de la sección 
    if y_position < 200:
     y_position = add_new_page()
    else:
     y_position -= 100  # Ajuste para agregar espacio entre secciones

     # Agregar módulo de qPCR Target Information
    qpcr_target_module_title = "qPCR Target Information"
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, y_position, qpcr_target_module_title)
    for qpcr_data in datos_qpcr_target:
     if y_position < 200:
        y_position = add_new_page()
    c.drawString(100, y_position - 20, f"Gene Symbol: {qpcr_data.gene_symbol}")
    c.drawString(100, y_position - 40, f"Multiplex Efficiency and LOD for Each Assay: {qpcr_data.multiplex_efficiency_lod}")
    c.drawString(100, y_position - 60, f"Sequence Accession Number: {qpcr_data.sequence_accession_number}")
    c.drawString(100, y_position - 80, f"Amplicon Location: {qpcr_data.amplicon_location}")
    c.drawString(100, y_position - 100, f"Amplicon Length: {qpcr_data.amplicon_length}")
    c.drawString(100, y_position - 120, f"In Silico Specificity Screening: {qpcr_data.in_silico_specificity_screening}")
    c.drawString(100, y_position - 140, f"Pseudogenes, Retropseudogenes, or Other Homologs: {qpcr_data.pseudogenes_homologs}")
    c.drawString(100, y_position - 160, f"Sequence Alignment: {qpcr_data.sequence_alignment}")
    c.drawString(100, y_position - 180, f"Amplicon Secondary Structure Analysis: {qpcr_data.amplicon_secondary_structure_analysis}")
    c.drawString(100, y_position - 200, f"Primer Location by Exon or Intron: {qpcr_data.primer_location_exon_intron}")
    c.drawString(100, y_position - 220, f"Splicing Variants Targeted: {qpcr_data.splicing_variants_targeted}")
    y_position -= 240  # Bajar la posición después de cada conjunto de datos de qPCR Target Information
    y_position -= 20  # Espacio vertical adicional entre cada conjunto de datos de qPCR Target Information

    
     # Espacio vertical adicional antes de la sección 
    if y_position < 200:
     y_position = add_new_page()
    else:
     y_position -= 100  # Ajuste para agregar espacio entre secciones

     # Agregar módulo de qPCR Primers
    qpcr_primers_module_title = "qPCR Primers"
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, y_position, qpcr_primers_module_title)
    for primer_data in datos_qpcr_primers:
        if y_position < 200:
            y_position = add_new_page()
        c.drawString(100, y_position - 20, f"Forward sequence: {primer_data.forward_sequence}")
        c.drawString(100, y_position - 40, f"Reverse sequence: {primer_data.reverse_sequence}")
        c.drawString(100, y_position - 60, f"RTPrimerDB Identification Number: {primer_data.rtprimerdb_id}")
        c.drawString(100, y_position - 80, f"Probe Sequences: {primer_data.probe_sequences}")
        c.drawString(100, y_position - 100, f"Modification Location and Identity: {primer_data.modification_location_identity}")
        c.drawString(100, y_position - 120, f"Oligo Manufacturer: {primer_data.oligo_manufacturer}")
        c.drawString(100, y_position - 140, f"Purification Method: {primer_data.purification_method}")
        y_position -= 160  # Bajar la posición después de cada conjunto de datos de qPCR Primers
        y_position -= 20  # Espacio vertical adicional entre cada conjunto de datos de qPCR Primers


    # Espacio vertical adicional antes de la sección 
    if y_position < 200:
     y_position = add_new_page()
    else:
     y_position -= 100  # Ajuste para agregar espacio entre secciones

    # Agregar módulo de qPCR Protocol
    qpcr_protocol_module_title = "qPCR Protocol"
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, y_position, qpcr_protocol_module_title)
    for protocol_data in datos_qpcr_protocol:
        if y_position < 200:
            y_position = add_new_page()
        c.drawString(100, y_position - 20, f"Reaction Conditions: {protocol_data.reaction_conditions}")
        c.drawString(100, y_position - 40, f"Reaction Volume and DNA Quantity: {protocol_data.reaction_volume_dna_quantity}")
        c.drawString(100, y_position - 60, f"Primer, Probe, Mg++, and Dntp Concentrations: {protocol_data.primer_probe_concentrations}")
        c.drawString(100, y_position - 80, f"Polymerase Identity and Concentration: {protocol_data.polymerase_identity_concentration}")
        c.drawString(100, y_position - 100, f"Buffer/Kit Identity and Manufacturer: {protocol_data.buffer_kit_identity_manufacturer}")
        c.drawString(100, y_position - 120, f"Exact Chemical Constitution of the Buffer: {protocol_data.buffer_exact_chemical_constitution}")
        c.drawString(100, y_position - 140, f"Additives: {protocol_data.additives}")
        c.drawString(100, y_position - 160, f"Plates/Tubes Manufacturer and Catalog Number: {protocol_data.plates_tubes_manufacturer_catalog}")
        c.drawString(100, y_position - 180, f"Thermocycling Parameters: {protocol_data.thermocycling_parameters}")
        c.drawString(100, y_position - 200, f"Reaction Configuration: {protocol_data.reaction_configuration}")
        c.drawString(100, y_position - 220, f"qPCR Instrument Manufacturer: {protocol_data.qpcr_instrument_manufacturer}")
        c.drawString(100, y_position - 240, f"Reaction Quality Control: {protocol_data.reaction_quality_control}")
        y_position -= 260  # Bajar la posición después de cada conjunto de datos de qPCR Protocol
        y_position -= 20  # Espacio vertical adicional entre cada conjunto de datos de qPCR Protocol

    # Espacio vertical adicional antes de la sección
    if y_position < 200:
     y_position = add_new_page()
    else:
     y_position -= 100  # Ajuste para agregar espacio entre secciones

    # Agregar módulo de Data Analysis
    data_analysis_module_title = "Data Analysis"
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, y_position, data_analysis_module_title)
    for analysis_data in datos_data_analysis:
        if y_position < 200:
            y_position = add_new_page()
        c.drawString(100, y_position - 20, f"qPCR Analysis Program: {analysis_data.qpcr_analysis_program}")
        c.drawString(100, y_position - 40, f"Cq Method Determination: {analysis_data.cq_method_determination}")
        c.drawString(100, y_position - 60, f"Identification and Handling of Outliers: {analysis_data.identification_handling_outliers}")
        c.drawString(100, y_position - 80, f"NTC Results: {analysis_data.ntc_results}")
        c.drawString(100, y_position - 100, f"Justification of Number and Choice of Reference Genes: {analysis_data.reference_genes_justification}")
        c.drawString(100, y_position - 120, f"Normalization Method Description: {analysis_data.normalization_method_description}")
        c.drawString(100, y_position - 140, f"Number and Concordance of Biological Replicates: {analysis_data.biological_replicates_number_concordance}")
        c.drawString(100, y_position - 160, f"Number and Stage of Technical Replicates: {analysis_data.technical_replicates_number_stage}")
        c.drawString(100, y_position - 180, f"Repeatability (Intra-Assay Variation): {analysis_data.intra_assay_variation_repeatability}")
        c.drawString(100, y_position - 200, f"Reproducibility (Inter-Assay Variation, %CV): {analysis_data.inter_assay_variation_reproducibility}")
        c.drawString(100, y_position - 220, f"Power Analysis: {analysis_data.power_analysis}")
        c.drawString(100, y_position - 240, f"Statistical Methods for Significance of Results: {analysis_data.statistical_methods_significance}")
        c.drawString(100, y_position - 260, f"Software (source, version): {analysis_data.software_source_version}")
        c.drawString(100, y_position - 280, f"Cq or Submission of Raw Data using RDML: {analysis_data.cq_or_raw_data_rdml_submission}")
        y_position -= 300  # Bajar la posición después de cada conjunto de datos de Data Analysis
        y_position -= 20  # Espacio vertical adicional entre cada conjunto de datos de Data Analysis

    
    # Espacio vertical adicional antes de la sección 
    if y_position < 200:
     y_position = add_new_page()
    else:
     y_position -= 100  # Ajuste para agregar espacio entre secciones


    # Agregar módulo de Thermal Cycling Conditions
    thermal_cycling_module_title = "Thermal Cycling Conditions"
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, y_position, thermal_cycling_module_title)
    for tc_data in datos_thermal_cycling_conditions:
        if y_position < 200:
            y_position = add_new_page()
        c.drawString(100, y_position - 20, f"Equipment Used: {tc_data.equipment_used}")
        c.drawString(100, y_position - 40, f"Primers Used: {tc_data.primers_used}")
        c.drawString(100, y_position - 60, f"PCR Conditions: {tc_data.pcr_conditions}")
        c.drawString(100, y_position - 80, f"Reaction Volume: {tc_data.reaction_volume}")
        c.drawString(100, y_position - 100, f"Positive Control: {tc_data.positive_control}")
        c.drawString(100, y_position - 120, f"Negative Control: {tc_data.negative_control}")
        y_position -= 140  # Bajar la posición después de cada conjunto de datos de Thermal Cycling Conditions
        y_position -= 20  # Espacio vertical adicional entre cada conjunto de datos de Thermal Cycling Conditions


     # Espacio vertical adicional antes de la sección 
    if y_position < 200:
     y_position = add_new_page()
    else:
     y_position -= 100  # Ajuste para agregar espacio entre secciones


    # Agregar módulo de qPCR Validation
    qpcr_validation_module_title = "qPCR Validation"
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, y_position, qpcr_validation_module_title)
    for qpcr_validation_data in datos_qpcr_validation:
        if y_position < 200:
            y_position = add_new_page()
        c.drawString(100, y_position - 20, f"Optimization Evidence: {qpcr_validation_data.optimization_evidence}")
        c.drawString(100, y_position - 40, f"Specificity Evidence: {qpcr_validation_data.specificity_evidence}")
        c.drawString(100, y_position - 60, f"Cq of NCT for SYBR Green I: {qpcr_validation_data.cq_nct_for_sybr_green}")
        c.drawString(100, y_position - 80, f"Standard Curves with Slope and Intercept: {qpcr_validation_data.standard_curves_slope_intercept}")
        c.drawString(100, y_position - 100, f"PCR Efficiency Calculated from Slope: {qpcr_validation_data.pcr_efficiency_slope_calculation}")
        c.drawString(100, y_position - 120, f"Confidence Interval for PCR Efficiency: {qpcr_validation_data.pcr_efficiency_confidence_interval}")
        c.drawString(100, y_position - 140, f"R^2 of the Standard Curve: {qpcr_validation_data.r2_standard_curve}")
        c.drawString(100, y_position - 160, f"Linear Dynamic Range: {qpcr_validation_data.linear_dynamic_range}")
        c.drawString(100, y_position - 180, f"Cq Variation at the Lower Limit: {qpcr_validation_data.cq_variation_lower_limit}")
        c.drawString(100, y_position - 200, f"Confidence Intervals across the Full Range: {qpcr_validation_data.confidence_intervals_full_range}")
        c.drawString(100, y_position - 220, f"LOD Evidence: {qpcr_validation_data.lod_evidence}")
        c.drawString(100, y_position - 240, f"If Multiplex, Efficiency and LOD for Each Assay: {qpcr_validation_data.multiplex_efficiency_lod}")
        y_position -= 260  # Bajar la posición después de cada conjunto de datos de qPCR Validation
        y_position -= 20  # Espacio vertical adicional entre cada conjunto de datos de qPCR Validation


     # Espacio vertical adicional antes de la sección 
    if y_position < 200:
     y_position = add_new_page()
    else:
     y_position -= 100  # Ajuste para agregar espacio entre secciones


    # Agregar módulo de Real-Time PCR Data
    realtime_pcr_module_title = "Real-Time PCR Data"
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, y_position, realtime_pcr_module_title)
    for realtime_pcr_data in datos_realtime_pcr_data:
        if y_position < 200:
            y_position = add_new_page()
        c.drawString(100, y_position - 20, f"Data Analysis Software: {realtime_pcr_data.data_analysis_software}")
        c.drawString(100, y_position - 40, f"Quantification Method: {realtime_pcr_data.quantification_method}")
        c.drawString(100, y_position - 60, f"Raw Data: {realtime_pcr_data.raw_data}")
        y_position -= 80  # Bajar la posición después de cada conjunto de datos de Real-Time PCR Data
        y_position -= 20  # Espacio vertical adicional entre cada conjunto de datos de Real-Time PCR Data


    # Espacio vertical adicional antes de la sección 
    if y_position < 200:
     y_position = add_new_page()
    else:
     y_position -= 100  # Ajuste para agregar espacio entre secciones


    # Agregar módulo de Results and Analysis
    results_analysis_module_title = "Results and Analysis"
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, y_position, results_analysis_module_title)
    for results_analysis_data in datos_results_analysis:
        if y_position < 200:
            y_position = add_new_page()
        c.drawString(100, y_position - 20, f"Results Interpretation: {results_analysis_data.results_interpretation}")
        c.drawString(100, y_position - 40, f"Charts and Figures: {results_analysis_data.charts_figures}")
        y_position -= 60  # Bajar la posición después de cada conjunto de datos de Results and Analysis
        y_position -= 20  # Espacio vertical adicional entre cada conjunto de datos de Results and Analysis

    c.save()

    # Devolver el PDF como respuesta
    buffer.seek(0)
    response = make_response(buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=informe_experimento.pdf'
    return response

if __name__ == '__main__':
    app.run(debug=True)
