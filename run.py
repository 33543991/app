from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SubmitField, DateField
from wtforms.validators import DataRequired, Email, EqualTo
from flask_bcrypt import Bcrypt

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
    experiment_date = DateField('Experiment Date', format='%Y-%m-%d', validators=[DataRequired()])
    experiment_number = StringField('Experiment Number', validators=[DataRequired()])
    principal_investigator = StringField('Principal Investigator', validators=[DataRequired()])
    institution_lab = StringField('Institution (and Laboratory)', validators=[DataRequired()])
    submit = SubmitField('Enviar')

class GeneralInfoDataModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    experiment_date = db.Column(db.Date, nullable=False)
    experiment_number = db.Column(db.String(100), nullable=False)
    principal_investigator = db.Column(db.String(100), nullable=False)
    institution_lab = db.Column(db.String(100), nullable=False)

# Experimental Design
class ExperimentalDesignForm(FlaskForm):
    group_control_definition = StringField('Group Control Definition', validators=[DataRequired()])
    group_experimental_definition = StringField('Group Experimental Definition', validators=[DataRequired()])
    group_control_number = StringField('Group Control Number', validators=[DataRequired()])
    group_experimental_number = StringField('Group Experimental Number', validators=[DataRequired()])
    submit = SubmitField('Enviar')
    
class DesignDataModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_control_definition = db.Column(db.String(100), nullable=False)
    group_experimental_definition = db.Column(db.String(100), nullable=False)
    group_control_number = db.Column(db.Integer, nullable=False)
    group_experimental_number = db.Column(db.Integer, nullable=False)
    
# Sample
class SampleForm(FlaskForm):
    sample_type = StringField('Sample Type', validators=[DataRequired()])
    sample_description = TextAreaField('Description', validators=[DataRequired()])
    sample_volume_mass = StringField('Volume/Mass of Processed Sample', validators=[DataRequired()])
    sampling_procedure = StringField('Sampling Procedure', validators=[DataRequired()])
    freezing_method = StringField('Freezing Method', validators=[DataRequired()])
    fixation_method = StringField('Fixation Method', validators=[DataRequired()])
    storage_conditions = StringField('Storage Conditions and Duration', validators=[DataRequired()])
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
    extraction_procedure = StringField('Extraction Procedure and/or Instrumentation', validators=[DataRequired()])
    kit_details = StringField('Kit Details and Any Modifications', validators=[DataRequired()])
    additional_reagents = StringField('Source of Additional Reagents Used', validators=[DataRequired()])
    dnase_rnase_treatment = StringField('Details of DNase or RNase Treatment', validators=[DataRequired()])
    contamination_evaluation = StringField('Contamination Evaluation (DNA or RNA)', validators=[DataRequired()])
    nucleic_acid_quantification_method = StringField('Nucleic Acid Quantification Method (Instrument and Method)', validators=[DataRequired()])
    nucleic_acid_purity = StringField('Nucleic Acid Purity (A260/A280)', validators=[DataRequired()])
    nucleic_acid_yield = StringField('Nucleic Acid Yield', validators=[DataRequired()])
    integrity_assessment_method = StringField('Integrity Assessment Method (RNA)', validators=[DataRequired()])
    rin_rqi_cq_details = StringField('RIN/RQI or Cq of 3’ and 5’ Transcriptions', validators=[DataRequired()])
    electrophoresis_traces = StringField('Electrophoresis Traces', validators=[DataRequired()])
    inhibition_testing = StringField('Inhibition Testing (Cq dilutions, peaks, or others)', validators=[DataRequired()])
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
    reaction_conditions = StringField('Reaction Conditions', validators=[DataRequired()])
    rna_quantity_volume = StringField('RNA Quantity and Reaction Volume', validators=[DataRequired()])
    oligo_priming_concentration = StringField('Oligo Priming Concentration', validators=[DataRequired()])
    reverse_transcription_concentration = StringField('Reverse Transcription Concentration', validators=[DataRequired()])
    primer_concentration = StringField('Primer Concentration', validators=[DataRequired()])
    temperature_time = StringField('Temperature and Time', validators=[DataRequired()])
    reagent_manufacturer_catalog = StringField('Reagent Manufacturer and Catalog Numbers', validators=[DataRequired()])
    cqs_with_without_reverse_transcription = StringField('Cqs with and without Reverse Transcription', validators=[DataRequired()])
    dna_storage_conditions = StringField('DNA Storage Conditions', validators=[DataRequired()])
    commercial_brand = StringField('Commercial Brand', validators=[DataRequired()])
    batch = StringField('Batch', validators=[DataRequired()])
    submit = SubmitField('Enviar')

class ReverseTranscriptionDataModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reaction_conditions = db.Column(db.String(100), nullable=False)
    rna_quantity_volume = db.Column(db.String(100), nullable=False)
    oligo_priming_concentration = db.Column(db.String(100), nullable=False)
    reverse_transcription_concentration = db.Column(db.String(100), nullable=False)
    primer_concentration = db.Column(db.String(100), nullable=False)
    temperature_time = db.Column(db.String(100), nullable=False)
    reagent_manufacturer_catalog = db.Column(db.String(100), nullable=False)
    cqs_with_without_reverse_transcription = db.Column(db.String(100), nullable=False)
    dna_storage_conditions = db.Column(db.String(100), nullable=False)
    commercial_brand = db.Column(db.String(100), nullable=False)
    batch = db.Column(db.String(100), nullable=False)

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
    primer_sequences = StringField('Primer Sequences', validators=[DataRequired()])
    rtprimerdb_id = StringField('RTPrimerDB Identification Number', validators=[DataRequired()])
    probe_sequences = StringField('Probe Sequences (if applicable)')
    modification_location_identity = StringField('Modification Location and Identity', validators=[DataRequired()])
    oligo_manufacturer = StringField('Oligo Manufacturer', validators=[DataRequired()])
    purification_method = StringField('Purification Method', validators=[DataRequired()])
    submit = SubmitField('Enviar')

class qPCRPrimersDataModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    primer_sequences = db.Column(db.String(100), nullable=False)
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.contrasena, password): 
            session['username'] = username
            return redirect(url_for('index')) 
        else:
            return render_template('login.html', message='Usuario o contraseña incorrectos')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

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
@app.route('/info', methods=['GET', 'POST'])
def info():
    form = GeneralInfoForm()
    if form.validate_on_submit():
        try:
            general_info_data = GeneralInfoDataModel(
                experiment_date=form.experiment_date.data,
                experiment_number=form.experiment_number.data,
                principal_investigator=form.principal_investigator.data,
                institution_lab=form.institution_lab.data
            )
            db.session.add(general_info_data)
            db.session.commit()
            flash('General information successfully recorded!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'An error occurred while recording general information: {str(e)}', 'danger')

    return render_template('info.html', form=form)


# Experimental Design
@app.route('/design', methods=['GET', 'POST'])
def design():
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
                rna_quantity_volume=form.rna_quantity_volume.data,
                oligo_priming_concentration=form.oligo_priming_concentration.data,
                reverse_transcription_concentration=form.reverse_transcription_concentration.data,
                primer_concentration=form.primer_concentration.data,
                temperature_time=form.temperature_time.data,
                reagent_manufacturer_catalog=form.reagent_manufacturer_catalog.data,
                cqs_with_without_reverse_transcription=form.cqs_with_without_reverse_transcription.data,
                dna_storage_conditions=form.dna_storage_conditions.data,
                commercial_brand=form.commercial_brand.data,
                batch=form.batch.data
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
    form = qPCRPrimersForm()
    if form.validate_on_submit():
        try:
            qpcr_primer_data = qPCRPrimersDataModel(
                primer_sequences=form.primer_sequences.data,
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
        reverse_data = ReverseTranscriptionDataModel.query.all()  # Suponiendo que tienes un modelo llamado ReverseTranscriptionDataModel para tus datos de transcripción inversa
        target_data = qPCRTargetInfoDataModel.query.all()  # Modelo de datos para qPCR Target Information
        primer_data = qPCRPrimersDataModel.query.all()  # Modelo de datos para qPCR Primers
        protocol_data = qPCRProtocolDataModel.query.all()
        thermal_data = ThermalCyclingConditionsDataModel.query.all()
        validation_data = qPCRValidationDataModel.query.all()
        data_analysis_data = DataAnalysisModel.query.all()
        results_data = ResultsAnalysisModel.query.all()
        real_time_pcr_data = RealTimePCRDataModel.query.all()
        return render_template('report.html', username=username, general_info_data=general_info_data, design_data=design_data, sample_data=sample_data, extraction_data=extraction_data, reverse_data=reverse_data, target_data=target_data, primer_data=primer_data, protocol_data=protocol_data, thermal_data=thermal_data, validation_data=validation_data, data_analysis_data=data_analysis_data, results_data=results_data, real_time_pcr_data=real_time_pcr_data)
    else:
        # Manejo si el usuario no ha iniciado sesión
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
