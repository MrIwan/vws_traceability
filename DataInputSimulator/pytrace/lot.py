from basyx.aas import model
from .global_variables import *
from .helper import *
from .base_aas import BaseAAS

import random
from datetime import datetime, timedelta

class Lot(BaseAAS):
    def __init__(self, material_id: str, lot_id: str) -> None:
        self.material_id = material_id
        self.lot_id = lot_id

        aas_id = f'{id_url}mat/{material_id}/batch/{lot_id}/aas'

        aas = self.init_aas(aas_id)

        if not aas:
            asset_information = model.AssetInformation(
                asset_kind=model.AssetKind.INSTANCE,
                global_asset_id=f'{id_url}mat/{material_id}/batch/{lot_id}'
            )

            self.aas = model.AssetAdministrationShell(
                id_ = aas_id,
                id_short = f'Batch_{lot_id}',
                asset_information = asset_information
            )

            self.add_sm(
                id_=f'{id_url}mat/{material_id}/batch/{lot_id}/batch/sm',
                id_short='Lot'
            )
            self.add_sm_el_to_sm(
                'Lot',
                model.Property(
                    id_short='Status',
                    value_type=model.datatypes.String,
                    value='finished'
                )
            )

            self.add_sm(
                id_ = f'{id_url}mat/{material_id}/run/{lot_id}/batch/sm',
                id_short='Runs'
            )

            post_aas(self.aas)
        
        else:
            self.aas = aas 


    def add_run(self) -> None:
        sm_runs = self.get_sm('Runs')
        existing_runs = [el for el in sm_runs.submodel_element if el.id_short.startswith('Run_')]
        if existing_runs:
            max_run_id = max(int(run.id_short.split('_')[1]) for run in existing_runs)
            new_run_id = max_run_id + 1
        else:
            new_run_id = 1

        smc_run = model.SubmodelElementCollection(id_short=f'Run_{new_run_id}')
        sm_runs.submodel_element.add(smc_run)
        post_sm(sm_runs, True)


    def run_add_step(self, run_number: int = -1) -> None:
        sm_runs = self.get_sm('Runs')
        existing_runs = [el for el in sm_runs.submodel_element if el.id_short.startswith('Run_')]
        
        try:
            current_run: model.SubmodelElementCollection  = existing_runs[run_number]
        except:
            raise ValueError("No current run. Please add a run first.")
        
        step_id = len(current_run.value) + 1
        smc_step = model.SubmodelElementCollection(id_short=f'Step_{step_id}')
        
        current_run.value.add(smc_step)
        post_sm(sm_runs, True)


    def step_add_property(self, prop: model.Property, run_number: int = -1, step_number: int =  -1) -> None:
        sm_runs = self.get_sm('Runs')
        existing_runs = [el for el in sm_runs.submodel_element if el.id_short.startswith('Run_')]
        
        try:
            current_run: model.SubmodelElementCollection  = existing_runs[run_number]
            existing_steps = [el for el in current_run if el.id_short.startswith('Step_')]
            current_step: model.SubmodelElementCollection = existing_steps[step_number]
        except:
            raise ValueError("No current run. Please add a run first.")
        
        current_step.value.add(prop)
        post_sm(sm_runs, True)


    def step_add_bom_material(self, url: str, ist_wert: float = None, soll_wert: float = None, run_number: int = -1, step_number: int = -1, component_number: int = -1) -> None:
        sm_runs = self.get_sm('Runs')

        try:
            existing_runs = [el for el in sm_runs.submodel_element if el.id_short.startswith('Run_')]
            current_run: model.SubmodelElementCollection  = existing_runs[run_number]
            existing_steps = [el for el in current_run if el.id_short.startswith('Step_')]
            current_step: model.SubmodelElementCollection = existing_steps[step_number]
        except:
            raise ValueError("No current run. Please add a run first.")
        
        smc_bom = next((el for el in current_step.value if el.id_short == 'ProcessBom'), None)
        if smc_bom is None:
            smc_bom = model.SubmodelElementCollection(id_short='ProcessBom')
            current_step.value.add(smc_bom)

        smc_components = [el for el in smc_bom if el.id_short.startswith('Component_')]
        new_component_id = 0
        if smc_components:
            new_component_id = len(smc_components)
        # new_sm_component_number = 0
        # if smc_component is None:
        #     smc_component = model.SubmodelElementCollection(id_short='Component_0')

        new_component = model.SubmodelElementCollection(
            id_short = f'Component_{new_component_id}'
        )
        
        new_component.value.add(model.ReferenceElement(
            id_short=f'UsedComponentRef',
            value=create_model_reference_from_global_id(url)
        ))

        if ist_wert:
            new_component.value.add(
                model.Property(
                    id_short='SollWert',
                    value_type=model.datatypes.Float,
                    value=ist_wert
                )
            )

        if soll_wert:
            new_component.value.add(
                model.Property(
                    id_short='IstWert',
                    value_type=model.datatypes.Float,
                    value=soll_wert
                )
            )
        
        smc_bom.value.add(new_component)
        post_sm(sm_runs, True)


    def step_add_prod_material(self, url: str, run_number: int = -1, step_number: int = -1) -> None:
        sm_runs = self.get_sm('Runs')

        try:
            existing_runs = [el for el in sm_runs.submodel_element if el.id_short.startswith('Run_')]
            current_run = existing_runs[run_number]
            existing_steps = [el for el in current_run if el.id_short.startswith('Step_')]
            current_step: model.SubmodelElementCollection = existing_steps[step_number]
        except:
            raise ValueError("No current run. Please add a run first.")
        
        smc_produced = next((el for el in current_step.value if el.id_short == 'ProducedMaterial'), None)
        if smc_produced is None:
            smc_produced = model.SubmodelElementCollection(id_short='ProducedMaterial')
            current_step.value.add(smc_produced)

        new_product_id = len(smc_produced.value)

        new_product = model.SubmodelElementCollection(
            id_short = f'Product_{new_product_id}'
        )
        
        new_product.value.add(model.ReferenceElement(
            id_short=f'ProducedMaterialRef',
            value=create_model_reference_from_global_id(url)
        ))
        
        smc_produced.value.add(new_product)
        post_sm(sm_runs, True)

    def step_add_process_parameter(self, parameter_name: str, nominal_value: any = None, actual_value: any = None, run_number: int = -1, step_number: int = -1) -> None:
        sm_runs = self.get_sm('Runs')

        try:
            existing_runs = [el for el in sm_runs.submodel_element if el.id_short.startswith('Run_')]
            current_run: model.SubmodelElementCollection = existing_runs[run_number]
            existing_steps = [el for el in current_run if el.id_short.startswith('Step_')]
            current_step: model.SubmodelElementCollection = existing_steps[step_number]
        except:
            raise ValueError("No current run. Please add a run first.")
        
        smc_process_parameters = next((el for el in current_step.value if el.id_short == 'ProcessParameters'), None)
        if smc_process_parameters is None:
            smc_process_parameters = model.SubmodelElementCollection(id_short='ProcessParameters')
            current_step.value.add(smc_process_parameters)

        existing_parameters = [el for el in smc_process_parameters.value if el.id_short.startswith('ProcessParameter_')]
        new_parameter_id = len(existing_parameters)

        new_parameter = model.SubmodelElementCollection(
            id_short=f'ProcessParameter_{parameter_name}'
        )

        if nominal_value is not None:
            new_parameter.value.add(
                model.Property(
                    id_short=f'Nominal{parameter_name}',
                    value_type=type(nominal_value),
                    value=nominal_value
                )
            )

        if actual_value is not None:
            new_parameter.value.add(
                model.Property(
                    id_short=f'Actual{parameter_name}',
                    value_type=type(actual_value),
                    value=actual_value
                )
            )
        
        smc_process_parameters.value.add(new_parameter)
        post_sm(sm_runs, True)

    def step_add_time_series(self, parameter_name: str, time_series_name: str, num_points: int = 30, run_number: int = -1, step_number: int = -1) -> None:
        sm_runs = self.get_sm('Runs')

        try:
            existing_runs = [el for el in sm_runs.submodel_element if el.id_short.startswith('Run_')]
            current_run = existing_runs[run_number]
            existing_steps = [el for el in current_run if el.id_short.startswith('Step_')]
            current_step = existing_steps[step_number]
        except:
            raise ValueError("No current run or step. Please add a run and step first.")


        time_series_collection = model.SubmodelElementCollection(id_short=time_series_name)
        
        start_time = datetime.now()
        for i in range(num_points):
            timestamp = start_time + timedelta(minutes=i)
            
            # Generate random values
            temperature = round(random.uniform(15, 30), 1)
            humidity = random.randint(30, 80)
            air_quality = random.randint(0, 500)
            
            data_point = model.SubmodelElementCollection(id_short=f"t{i+1}")
            data_point.value.add(model.Property(id_short="time", value=timestamp.isoformat(), value_type=str))
            data_point.value.add(model.Property(id_short="Temperature", value=temperature, value_type=float))
            data_point.value.add(model.Property(id_short="Humidity", value=humidity, value_type=int))
            data_point.value.add(model.Property(id_short="AirQuality", value=air_quality, value_type=int))
            
            time_series_collection.value.add(data_point)

        current_step.value.add(time_series_collection)

        post_sm(sm_runs, True)
