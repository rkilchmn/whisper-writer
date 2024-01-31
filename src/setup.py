import os
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QCheckBox, QLabel, QLineEdit, QComboBox, QGridLayout, QGroupBox, QSpacerItem, QSizePolicy, QMessageBox, QInputDialog
from PyQt5.QtGui import QFont, QIcon
from settings import Settings

class SetupWindow(QWidget):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.checkboxes = {}
        self.textboxes = {}
        self.dropdowns = {}
        self.initUI()

    def initUI(self):
        self.setWindowTitle('WhisperWriter Setup')
        self.setGeometry(300, 300, 600, 400)
        self.setWindowIcon(QIcon(os.path.join('assets', 'ww-logo.ico')))

        main_layout = QVBoxLayout(self)
        grid_layout = QGridLayout()
        main_layout.addLayout(grid_layout)

        def makeTitleBold(groupBox):
            font = QFont()
            font.setBold(True)
            groupBox.setStyleSheet('QGroupBox::title {font: bold;}')
            groupBox.setFont(font)

        # Split settings into separate group boxes
        self.model_options_group = QGroupBox('Model Options')
        self.model_options_group.setLayout(QVBoxLayout())
        makeTitleBold(self.model_options_group)
        
        self.recording_options_group = QGroupBox('Recording Options')
        self.recording_options_group.setLayout(QVBoxLayout())
        makeTitleBold(self.recording_options_group)
        
        self.post_processing_group = QGroupBox('Post Processing')
        self.post_processing_group.setLayout(QVBoxLayout())
        makeTitleBold(self.post_processing_group)
        
        self.misc_group = QGroupBox('Miscellaneous')
        self.misc_group.setLayout(QVBoxLayout())
        makeTitleBold(self.misc_group)

        grid_layout.addWidget(self.model_options_group, 0, 0)
        grid_layout.addWidget(self.recording_options_group, 0, 1)
        grid_layout.addWidget(self.post_processing_group, 1, 0)
        grid_layout.addWidget(self.misc_group, 1, 1)

        self.createInputs(self.settings.config, main_layout)
        
        # Add spacers to the bottom of each group box to even out appearance
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.model_options_group.layout().addSpacerItem(spacer)
        self.recording_options_group.layout().addSpacerItem(spacer)
        self.post_processing_group.layout().addSpacerItem(spacer)
        self.misc_group.layout().addSpacerItem(spacer)

        # Save Button
        save_btn = QPushButton('Save Settings', self)
        save_btn.clicked.connect(self.saveSettings)
        main_layout.addWidget(save_btn)

        self.setLayout(main_layout)

    def createInputs(self, config, layout, prefix='', level=0):
        for key, value in config.items():
            full_key = f'{prefix}{key}'
            is_dict = isinstance(value, dict)
            is_bool = isinstance(value, bool)
            is_alphanumeric = isinstance(value, (str, int, float)) or value is None

            if 'model_options' in full_key:
                group_layout = self.model_options_group.layout()
            elif 'recording_options' in full_key:
                group_layout = self.recording_options_group.layout()
            elif 'post_processing' in full_key:
                group_layout = self.post_processing_group.layout()
            elif 'misc' in full_key:
                group_layout = self.misc_group.layout()
            else:
                group_layout = layout

            # Formatting label based on the level
            label_text = key.replace('_', ' ').capitalize()
            if is_dict:
                self.createCategoryLabel(label_text, group_layout, level) if level != 0 else None
                self.createInputs(value, group_layout, prefix=f'{full_key}.', level=level+1)
            elif is_bool:
                self.createCheckbox(full_key, label_text, value, group_layout)
            elif is_alphanumeric:
                if full_key in self.settings.dropdown_options:
                    self.createDropdown(full_key, label_text, value, group_layout)
                else:
                    self.createTextbox(full_key, label_text, value, group_layout)

    def createCategoryLabel(self, label_text, layout, level):
        label = QLabel(label_text)
        font = QFont()
        if level == 1:  # Second-level category - italics
            font.setItalic(True)
        label.setFont(font)
        layout.addWidget(label)

    def createCheckbox(self, key, label_text, value, layout):
        checkbox = QCheckBox(label_text)
        checkbox.setChecked(value)
        layout.addWidget(checkbox)
        self.checkboxes[key] = checkbox

    def createDropdown(self, key, label_text, value, layout):
        label = QLabel(label_text)
        layout.addWidget(label)
        dropdown = QComboBox(self)
        dropdown.addItems(self.settings.dropdown_options[key])
        dropdown.setCurrentText(value)
        layout.addWidget(dropdown)
        self.dropdowns[key] = dropdown

    def createTextbox(self, key, label_text, value, layout):
        label = QLabel(label_text)
        layout.addWidget(label)
        line_edit = QLineEdit(self)
        line_edit.setText(str(value)) if value is not None else None
        layout.addWidget(line_edit)
        self.textboxes[key] = line_edit

    def saveSettings(self):
        # Update settings from checkboxes
        for key, checkbox in self.checkboxes.items():
            keys = key.split('.')
            self.updateConfig(self.settings.config, keys, checkbox.isChecked())

        # Update settings from textboxes
        for key, textbox in self.textboxes.items():
            keys = key.split('.')
            value = textbox.text()
            # Convert to int or float if applicable
            if value.isdigit():
                value = int(value)
            else:
                try:
                    value = float(value)
                except ValueError:
                    pass
            self.updateConfig(self.settings.config, keys, value)

        # Update settings from dropdowns
        for key, dropdown in self.dropdowns.items():
            keys = key.split('.')
            self.updateConfig(self.settings.config, keys, dropdown.currentText())

        self.settings.save_config()
        
        if self.checkboxes['model_options.use_api'].isChecked():
            # Check if .env file exists and contains the API key
            env_path = os.path.join(os.getcwd(), '.env')
            if not self.envHasKey(env_path):
                api_key, ok = QInputDialog.getText(self, 'API Key Required', 
                                                   'Please enter your OpenAI API key. You can retrieve it from https://platform.openai.com/api-keys')
                if ok and api_key:
                    self.configureEnvFile(api_key, env_path)
                else:
                    QMessageBox.warning(self, 'API Key Missing', 
                                        'The OpenAI API key is required to use the API.')
        
        self.close()

    def envHasKey(self, env_path):
        if os.path.exists(env_path):
            with open(env_path, 'r') as file:
                for line in file:
                    if line.startswith('OPENAI_API_KEY=') and len(line) > 15:
                        return True
        return False

    def configureEnvFile(self, api_key, env_path):
        with open(env_path, 'w') as file:
            file.write('# Once you add your API key below, make sure to not share it with anyone! The API key should remain private.\n')
            file.write(f'OPENAI_API_KEY={api_key}\n')
        QMessageBox.information(self, 'Configuration Success', 
                                'Your API key has been configured successfully. You can modify it in the .env file.')

    def updateConfig(self, config, keys, value):
        key = keys.pop(0)
        if len(keys) == 0:
            config[key] = value
        else:
            if key not in config:
                config[key] = {}
            self.updateConfig(config[key], keys, value)
        
def run_setup(settings):
    app = QApplication(sys.argv)
    setup_window = SetupWindow(settings)
    setup_window.show()
    app.exec_()

if __name__ == '__main__':
    default_config_path = os.path.join('src', 'default_config.yaml')
    user_config_path = os.path.join('src', 'config.yaml')
    
    settings = Settings(default_config_path, user_config_path)
    
    run_setup(settings)
