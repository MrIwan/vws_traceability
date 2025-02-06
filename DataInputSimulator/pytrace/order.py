from basyx.aas import model

from .global_variables import *

from .helper import *

from .base_aas import BaseAAS

class ProductionOrder(BaseAAS):

    def __init__(self, 
                 material_id: str,
                 order_id: str,
                 prod_type_ref: str) -> None:
        
        
        self.material_id = material_id
        self.batch_id = order_id

        aas_id = f'{id_url}mat/{material_id}/order/{order_id}/aas'

        aas = self.init_aas(aas_id)

        if not aas:

            ## AAS erstellen
            asset_information = model.AssetInformation(
                asset_kind=model.AssetKind.INSTANCE,
                global_asset_id=f'{id_url}mat/{material_id}/order/{order_id}'
            )

            self.aas = model.AssetAdministrationShell(
                id_=f'{id_url}mat/{material_id}/order/{order_id}/aas',  # set identifier,
                id_short=f'Order_{order_id}',
                asset_information=asset_information
            )

            ## SM für allgemeine Informationen hinzufügen
            self.add_sm(
                id_=f'{id_url}mat_{material_id}/order/sm/order/{order_id}',
                id_short='Order'
            ) 

            self.add_sm_el_to_sm(
                sm_name='Order',
                el=model.Property(
                    id_short='Status',
                    value_type=model.datatypes.String,
                    value='finished'
                )
            )

            self.add_sm_el_to_sm(
                sm_name='Order',
                el=model.ReferenceElement(
                    id_short='ProductTypeReference',
                    value=create_model_reference_from_global_id(prod_type_ref)
                )
            )
                
            post_aas(self.aas)

        else:
            self.aas = aas

    def add_batch_ref(self, ref: str):
        sm_order = self.get_sm('Order')

        # Smc holen oder erstellen
        smc_refs: model.SubmodelElementCollection = next((el for el in sm_order if el.id_short == 'BatchReferences'), None)
        if smc_refs is None:
            smc_refs = model.SubmodelElementCollection(
                id_short='BatchReferences'
            )
            sm_order.submodel_element.add(smc_refs)

        existing_batches = [el for el in smc_refs if el.id_short.startswith('Batch_')]
        if existing_batches:
            max_batch_id = max(int(batch.id_short.split('_')[1]) for batch in existing_batches)
            new_batch_id = max_batch_id + 1
        else: 
            new_batch_id = 1

        smc_refs.value.add(
            model.ReferenceElement(
                id_short=f'Batch_{new_batch_id}',
                value=create_model_reference_from_global_id(ref)
            )
        )

        post_sm(sm_order, True)