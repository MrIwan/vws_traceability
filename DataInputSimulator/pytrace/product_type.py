from basyx.aas import model

from pytrace.global_variables import *

from .helper import *

from .base_aas import BaseAAS


####### NICHT WEITER ENTWICKELT ########


class ProductType(BaseAAS):
    def __init__(self, 
                 material_id, 
                 obj_store: model.DictObjectStore,
                 product_name: str = 'product') -> None:
        
        self.material_id = material_id
    
        self.obj_store = obj_store
        self.product_name =product_name

        # Erstelle die aas
        asset_information = model.AssetInformation(
            asset_kind=model.AssetKind.INSTANCE,
            global_asset_id=f'{id_url}mat/{material_id}'
        )

        aas = model.AssetAdministrationShell(
            id_=f'{id_url}mat/{material_id}/aas',
            id_short=f'{product_name}Type',
            asset_information = asset_information
        )

        self.aas = aas
        self.sm_bop = None
        self.smc_current_step = None
        obj_store.add(aas)

    def add_sm_nameplate(self):
        # Erstelle sm mit Nameplate
        sm = model.Submodel(
            id_ = f'{id_url}mat_{self.material_id}/sm/nameplate',
            id_short='DetailedDescription',
        )

        sm.submodel_element.add(
            model.Property(
                id_short = 'Name',
                value_type=model.datatypes.String,
                value=f'{self.product_name}'
            )
        )

        self.aas.submodel.add(model.ModelReference.from_referable(sm))
        self.obj_store.add(sm)


    def add_bob_step(self,
        process_id: int,
        process_name: str,
        process_description: str,
        planned_process_time: float):

    # Erstelle sm mit bop falls es noch nicht existiert
        if self.sm_bop == None:
            self.sm_bop = model.Submodel(
                id_ = f'{id_url}mat_{self.material_id}/sm/bop',
                id_short='BillOfProcess',
            )

            self.aas.submodel.add(model.ModelReference.from_referable(self.sm_bop))
            self.obj_store.add(self.sm_bop)

        # Determine the next step number
        existing_steps = [smc for smc in self.sm_bop.submodel_element if smc.id_short.startswith('ProcessStep_')]
        step = len(existing_steps) + 1

        # create new Step 
        smc_step = model.SubmodelElementCollection(
            id_short=f'ProcessStep_{step}'
        )

        smc_step.value.add(
            model.Property(
                id_short='ProcessId',
                value_type=model.datatypes.Int,
                value=process_id
            )
        )

        smc_step.value.add(
            model.Property(
                id_short='ProcessName',
                value_type=model.datatypes.String,
                value=process_name
            )
        )

        smc_step.value.add(
            model.Property(
                id_short='ProcessDescription',
                value_type=model.datatypes.String,
                value=process_description
            )
        )

        smc_step.value.add(
            model.Property(
                id_short='PlannedProcessTime',
                value_type=model.datatypes.Float,
                value=planned_process_time
            )
        )

        self.sm_bop.submodel_element.add(
            smc_step
        )
        self.smc_current_step = smc_step


    def add_product_parameters(
            self,
            nominal_percentage_share: float,
            product_type_ref: str
            ):

        if self.smc_current_step is None:
            print('Es gibt keinen current_step')
            return
        
        smc_pp = next((smc for smc in self.smc_current_step.value if smc.id_short == 'ProductParameters'), None)

        if smc_pp is None:
            smc_pp = model.SubmodelElementCollection(
                id_short='ProductParameters'
            )
            self.smc_current_step.value.add(smc_pp)
            component_number = 0
        else:
            component_number = max([int(smc.id_short.split('_')[1]) for smc in smc_pp.value if smc.id_short.startswith('Component_')], default=-1) + 1

        smc_component = model.SubmodelElementCollection(
            id_short=f'Component_{component_number}'
        )

        smc_component.value.add(
            model.Property(
                id_short='NominalPercentageShare',
                value_type=model.datatypes.Float,
                value=nominal_percentage_share
            )
        )

        smc_component.value.add(
            model.ReferenceElement(
                id_short='ProductTypeRef',
                value=create_model_reference_from_global_id(product_type_ref)
            )
        )

        smc_pp.value.add(smc_component)


    def add_process_parameter(self, property: model.Property):
        if self.smc_current_step is None:
            print('Es gibt keinen current_step')
            return
        
        smc_process_params = next((smc for smc in self.smc_current_step.value if smc.id_short == "ProcessParameters"), None)

        if smc_process_params is None:
            smc_process_params = model.SubmodelElementCollection(
                id_short="ProcessParameters"
            )
            self.smc_current_step.value.add(smc_process_params)

        smc_process_params.value.add(property)

    