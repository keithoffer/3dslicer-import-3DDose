import os
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import numpy as np

class import3DDose(ScriptedLoadableModule):
  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Import3DDose"
    self.parent.categories = ["Importer"]
    self.parent.dependencies = []
    self.parent.contributors = ["Keith Offer (None)"]
    self.parent.helpText = """
A simple extension to import .3ddose files from DOSXYZnrc. See See <a href="https://github.com/keithoffer/3DSlicer-Import3DDose">GitHub</a> for more information.
"""
    self.parent.acknowledgementText = ""

class import3DDoseWidget(ScriptedLoadableModuleWidget):
    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)

        # All the GUI components in the pane
        self.dose_options_collapsible_button = ctk.ctkCollapsibleButton()
        self.dose_options_collapsible_button.text = "Dose Options"
        self.layout.addWidget(self.dose_options_collapsible_button)
        self.dose_form_layout = qt.QFormLayout(self.dose_options_collapsible_button)

        self.import_dose_check_box = qt.QCheckBox()
        self.import_dose_check_box.setText("Import dose values")
        self.import_dose_check_box.checked = 1
        self.import_dose_check_box.setToolTip("Import the dose values in a .3ddose file")
        self.dose_form_layout.addWidget(self.import_dose_check_box)

        self.normalise_dose_check_box = qt.QCheckBox()
        self.normalise_dose_check_box.setText("Normalise dose values")
        self.normalise_dose_check_box.checked = 0
        self.normalise_dose_check_box.setToolTip(
            "Dose values in .3ddose files are typically very small (i.e. less than 1E-10). 3D Slicer isn't really designed to work with values this small, and it can lead to issues."
            "Turning this feature on normalises the results in the .3ddose file to a range of [0,1]. 3D Slicer handles these values much better, but you lose some information."
            "If this option is picked, the maximum value in the dose array before normalisation is printed to the console for use in un-normalising the data if needed.")
        self.dose_form_layout.addWidget(self.normalise_dose_check_box)

        self.overwrite_dose_volume_check_box = qt.QCheckBox()
        self.overwrite_dose_volume_check_box.setText("Overwrite existing volume")
        self.overwrite_dose_volume_check_box.checked = 0
        self.overwrite_dose_volume_check_box.setToolTip("Import the dose values into an existing volume")
        self.dose_form_layout.addWidget(self.overwrite_dose_volume_check_box)

        self.dose_volume_combo_box = slicer.qMRMLNodeComboBox()
        self.dose_volume_combo_box.nodeTypes = ["vtkMRMLScalarVolumeNode"]
        self.dose_volume_combo_box.selectNodeUponCreation = True
        self.dose_volume_combo_box.addEnabled = True
        self.dose_volume_combo_box.removeEnabled = True
        self.dose_volume_combo_box.noneEnabled = True
        self.dose_volume_combo_box.showHidden = False
        self.dose_volume_combo_box.showChildNodeTypes = False
        self.dose_volume_combo_box.setMRMLScene(slicer.mrmlScene)
        self.dose_volume_combo_box.setToolTip("Pick the output volume to store the dose")
        self.dose_volume_combo_box.setEnabled(False)
        self.dose_form_layout.addWidget(self.dose_volume_combo_box)

        self.uncertainty_options_collapsible_button = ctk.ctkCollapsibleButton()
        self.uncertainty_options_collapsible_button.text = "Uncertainty Options"
        self.layout.addWidget(self.uncertainty_options_collapsible_button)
        self.uncertainty_form_layout = qt.QFormLayout(self.uncertainty_options_collapsible_button)

        self.import_uncertainty_check_box = qt.QCheckBox()
        self.import_uncertainty_check_box.setText("Import uncertainty values")
        self.import_uncertainty_check_box.checked = 1
        self.import_uncertainty_check_box.setToolTip("Import the uncertainties in the .3ddose file")
        self.uncertainty_form_layout.addWidget(self.import_uncertainty_check_box)

        self.overwrite_uncertainty_volume_check_box = qt.QCheckBox()
        self.overwrite_uncertainty_volume_check_box.setText("Overwrite existing volume")
        self.overwrite_uncertainty_volume_check_box.checked = 0
        self.overwrite_uncertainty_volume_check_box.setToolTip("Import the uncertainty values into an existing volume")
        self.uncertainty_form_layout.addWidget(self.overwrite_uncertainty_volume_check_box)

        self.uncertainty_volume_combo_box = slicer.qMRMLNodeComboBox()
        self.uncertainty_volume_combo_box.nodeTypes = ["vtkMRMLScalarVolumeNode"]
        self.uncertainty_volume_combo_box.selectNodeUponCreation = True
        self.uncertainty_volume_combo_box.addEnabled = True
        self.uncertainty_volume_combo_box.removeEnabled = True
        self.uncertainty_volume_combo_box.noneEnabled = True
        self.uncertainty_volume_combo_box.showHidden = False
        self.uncertainty_volume_combo_box.showChildNodeTypes = False
        self.uncertainty_volume_combo_box.setMRMLScene(slicer.mrmlScene)
        self.uncertainty_volume_combo_box.setToolTip("Pick the output volume to store the uncertainties")
        self.uncertainty_volume_combo_box.setEnabled(False)
        self.uncertainty_form_layout.addWidget(self.uncertainty_volume_combo_box)

        self.import_button = qt.QPushButton("Import .3ddose")
        self.import_button.toolTip = "Browse for a .3ddose file to import"
        self.layout.addWidget(self.import_button)

        # Signals + slot connections
        self.import_button.clicked.connect(self.extension_invoked)
        self.overwrite_uncertainty_volume_check_box.clicked.connect(lambda state : self.uncertainty_volume_combo_box.setEnabled(state))
        self.overwrite_dose_volume_check_box.clicked.connect(lambda state: self.dose_volume_combo_box.setEnabled(state))

        # Add vertical spacer
        self.layout.addStretch(1)

    def extension_invoked(self):
        """
        Function called when the import button is pressed. Handles converting the GUI settings into parameters
        for the core logic function and calling it
        :return:
        """
        extension_logic = import3DDoseLogic()
        filepath = qt.QFileDialog.getOpenFileName(None, 'Load .3ddose file', '.', '*.3ddose')
        print(filepath)
        if filepath != '' and (self.import_dose_check_box.checked or self.import_uncertainty_check_box.checked):
            if self.overwrite_dose_volume_check_box.checked:
                dose_volume_node_to_overwrite = self.dose_volume_combo_box.currentNode()

                if not slicer.util.confirmYesNoDisplay("Are you sure you want to overwrite volume " + dose_volume_node_to_overwrite.GetName() + "?"):
                    return
            else:
                dose_volume_node_to_overwrite = None

            if self.overwrite_uncertainty_volume_check_box.checked:
                uncertainties_volume_node_to_overwrite = self.uncertainty_volume_combo_box.currentNode()

                if not slicer.util.confirmYesNoDisplay("Are you sure you want to overwrite volume " + uncertainties_volume_node_to_overwrite.GetName() + "?"):
                    return
            else:
                uncertainties_volume_node_to_overwrite = None

            extension_logic.run(filepath, normalise_dose=self.normalise_dose_check_box.checked,
                      import_dose = self.import_dose_check_box.checked,
                      import_uncertainty=self.import_uncertainty_check_box.checked,
                      dose_volume_node_to_overwrite=dose_volume_node_to_overwrite,
                      uncertainty_volume_node_to_overwrite=uncertainties_volume_node_to_overwrite)

class import3DDoseLogic(ScriptedLoadableModuleLogic):
    """
    Wrapper class for the main logic of this extension.
    """
    def run(self, filepath, import_dose = True, import_uncertainty = True, normalise_dose = False,
            dose_volume_node_to_overwrite=None,uncertainty_volume_node_to_overwrite=None):
        """
        Main function that imports the .3ddose file to vtkMRMLScalarVolumeNodes
        :param filepath: Path to the .3ddose file to be imported
        :param import_dose: Whether to create a volume containing the dose values in the .3ddose file
        :param import_uncertainty: Whether to create a volume containing the dose values in the .3ddose file
        :param normalise_dose: Whether to normalise the dose values in the volume to the range [0,1]
        :param dose_volume_node_to_overwrite: The volume to overwrite with the dose values (None implies create a new volume)
        :param uncertainty_volume_node_to_overwrite: The volume to overwrite with the uncertainty values (None implies create a new volume)
        :return: True if completed successfully
        """
        with open(filepath, 'r') as dosefile:
            try:
                # The code to read the .3ddose file mainly taken from https://gist.github.com/ftessier/086238152486749eab2f/
                # get voxel counts on first line
                nx, ny, nz = map(int, dosefile.readline().split())  # number of voxels along x, y, z
                Ng = (nx + 1) + (ny + 1) + (nz + 1)  # total number of voxel grid values (voxels+1)
                Nd = nx * ny * nz  # total number of data points

                # get voxel grid, dose and relative uncertanties
                data = list(map(float, dosefile.read().split()))  # read the rest of the file
                xgrid = data[:nx + 1]  # voxel boundaries in x (nx+1 values, 0 to nx)
                ygrid = data[nx + 1:nx + 1 + ny + 1]  # voxel boundaries in y (ny+1 values, nx+1 to nx+1+ny)
                zgrid = data[nx + 1 + ny + 1:Ng]  # voxel boundaries in z (nz+1 values, rest up to Ng-1)
                dose = data[Ng:Nd + Ng]  # flat array of Nd = nx*ny*nz dose values
                errs = data[Nd + Ng:]  # flat array of Nd = nx*ny*nz relative uncertainty values

                dose_array = np.flip(np.reshape(dose,(nz,nx,ny)),axis=0)
                if normalise_dose:
                    print("Max dose value before normalisation was " + str(dose_array.max()))
                    dose_array /= dose_array.max()
                uncertainty_array = np.flip(np.reshape(errs, (nz, nx, ny)),axis=0)
            except ValueError as e:
                slicer.util.errorDisplay("An error occured reading in the .3ddose file (is it a valid file)?\n"
                                        "Exception: " + str(e))
                return False

            del data, dose, errs # delete temp variables

        if not (all_equal_spacing(xgrid) and all_equal_spacing(ygrid) and all_equal_spacing(zgrid)):
            slicer.util.warningDisplay(
                """Voxel spacing changes along atleast one axis. The voxel size must be constant along each axis for 3DSlicer to display it correctly.
                Proceeding with the import, but spatially some information will be incorrect.""")

        volume_base_name = os.path.splitext(os.path.basename(filepath))[0]
        dose_volume_name = volume_base_name + '_dose'
        uncertainty_volume_name = volume_base_name + '_uncertainty'

        # Voxel spacing in each dimension (converted from mm to cm)
        dx = (xgrid[1] - xgrid[0])*10
        dy = (ygrid[1] - ygrid[0])*10
        dz = (zgrid[1] - zgrid[0])*10
        image_size = (nx,ny,nz)
        image_spacing = (dx, dy, dz)
        image_origin = (-0.5 * (nx - 1) * dx, -0.5 * (ny - 1) * dy, -0.5 * (nz - 1) * dz)

        app_logic = slicer.app.applicationLogic()
        selection_node = app_logic.GetSelectionNode()
        if import_dose:
            if dose_volume_node_to_overwrite is None:
                volume_node_dose = create_new_volume_from_array(dose_array, image_size, image_spacing, name=dose_volume_name)
            else:
                slicer.util.updateVolumeFromArray(dose_volume_node_to_overwrite, dose_array)
                update_visualisation_settings(dose_volume_node_to_overwrite, dose_array)
                dose_volume_node_to_overwrite.SetSpacing(image_spacing)
                dose_volume_node_to_overwrite.SetOrigin(image_origin)
                volume_node_dose = dose_volume_node_to_overwrite
            selection_node.SetActiveVolumeID(volume_node_dose.GetID())

        if import_uncertainty:
            if uncertainty_volume_node_to_overwrite is None:
                volume_node_uncertainty = create_new_volume_from_array(uncertainty_array, image_size, image_spacing, name=uncertainty_volume_name)
            else:
                slicer.util.updateVolumeFromArray(uncertainty_volume_node_to_overwrite, uncertainty_array)
                update_visualisation_settings(uncertainty_volume_node_to_overwrite, uncertainty_array)
                uncertainty_volume_node_to_overwrite.SetSpacing(image_spacing)
                uncertainty_volume_node_to_overwrite.SetOrigin(image_origin)
                volume_node_uncertainty = dose_volume_node_to_overwrite
            if not import_dose:
                selection_node.SetActiveVolumeID(volume_node_uncertainty.GetID())

        app_logic.PropagateVolumeSelection()
        return True

def all_equal_spacing(array):
    """
    Returns True if the 1D numpy array has a constant spacing between the values
    :param array: 1D array to be checked
    :return: If the spacing between each value in the array is constant
    """
    differences = list(np.ediff1d(array))
    return differences.count(differences[0]) == len(differences)

def update_visualisation_settings(volumeNode,array):
    """
    Updates the window, level and colormap for the volumeNode based on values in the array
    :param volumeNode: Volume node to be updated
    :param array: Array to derive optimal visualisation values
    :return:
    """
    displayNode = slicer.vtkMRMLScalarVolumeDisplayNode()
    displayNode.SetAutoWindowLevel(0)
    max_val = array.max()
    min_val = array.min()
    displayNode.SetWindowLevel(max_val - min_val, (max_val - min_val) / 2)
    slicer.mrmlScene.AddNode(displayNode)
    colorNode = slicer.util.getNode('Viridis')
    displayNode.SetAndObserveColorNodeID(colorNode.GetID())
    volumeNode.SetAndObserveDisplayNodeID(displayNode.GetID())

def create_new_volume_from_array(array,size,spacing,name=None):
    """
    Creates a new slicer volume from a 3D numpy array
    :param array: Values in the new volume
    :param size: Physical size of the new image volume
    :param spacing: Spacing between the voxels in the image
    :param name: Name to be given to the created volume
    :return: vtkMRMLScalarVolumeNode created
    """
    nx, ny, nz = size
    dx, dy, dz = spacing
    imageOrigin = (-0.5 * (nx - 1) * dx, -0.5 * (ny - 1) * dy, -0.5 * (nz - 1) * dz)
    voxelType = vtk.VTK_DOUBLE
    # Create an empty image volume
    imageData = vtk.vtkImageData()
    imageData.SetDimensions(size)
    imageData.AllocateScalars(voxelType, 1)
    # Create volume node
    volumeNode = slicer.vtkMRMLScalarVolumeNode()
    volumeNode.SetSpacing(spacing)
    volumeNode.SetOrigin(imageOrigin)
    # Add volume to scene
    slicer.mrmlScene.AddNode(volumeNode)
    update_visualisation_settings(volumeNode,array)
    volumeNode.CreateDefaultStorageNode()
    if name is not None:
        volumeNode.SetName(name)
    slicer.util.updateVolumeFromArray(volumeNode, array)
    return volumeNode

class import3DDoseTest(ScriptedLoadableModuleTest):
    def runTest(self):
        # No tests :(
        print("No tests")
