from basyx.aas import model
from .global_variables import *
from .helper import *
from .base_aas import BaseAAS

class Batch(BaseAAS):

    def __init__(self, 
                 material_id: str,
                 batch_id: str) -> None:
        
        
        self.material_id = material_id
        self.batch_id = batch_id

        aas_id = f'{id_url}mat/{material_id}/batch/{batch_id}/aas'

        aas = self.init_aas(aas_id)

        if not aas:

            ## AAS erstellen
            asset_information = model.AssetInformation(
                asset_kind=model.AssetKind.INSTANCE,
                global_asset_id=f'{id_url}mat/{material_id}/batch/{batch_id}'
            )

            self.aas = model.AssetAdministrationShell(
                id_=aas_id,  # set identifier,
                id_short=f'Batch_{batch_id}',
                asset_information=asset_information
            )

            ## SM für allgemeine Informationen hinzufügen
            self.add_sm(
                id_=f'{id_url}mat_{material_id}/batch/sm/batch/{batch_id}',
                id_short='Batch'
            ) 

            self.add_sm_el_to_sm(
                sm_name='Batch',
                el=model.Property(
                    id_short='Status',
                    value_type=model.datatypes.String,
                    value='finished'
                )
            )
            post_aas(self.aas)

        else: 
            self.aas = aas

    def add_lot_ref(self, ref: str):
        sm_batch = self.get_sm('Batch')

        # Smc holen oder erstellen
        smc_refs = next((el for el in sm_batch if el.id_short == 'LotReferences'), None)
        if smc_refs is None:
            smc_refs = model.SubmodelElementCollection(
                id_short='LotReferences'
            )
            sm_batch.submodel_element.add(smc_refs)

        existing_lots = [el for el in smc_refs if el.id_short.startswith('Lot_')]
        if existing_lots:
            max_lot_id = max(int(lot.id_short.split('_')[1]) for lot in existing_lots)
            new_lot_id = max_lot_id + 1
        else: 
            new_lot_id = 1

        smc_refs.value.add(
            model.ReferenceElement(
                id_short=f'Lot_{new_lot_id}',
                value=create_model_reference_from_global_id(ref)
            )
        )

        post_sm(sm_batch, True)