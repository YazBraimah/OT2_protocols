from opentrons import robot, labware, instruments


# labware setup
block = labware.load('nest_96_wellplate_100ul_pcr_full_skirt', '2')
plates = [labware.load('nest_96_wellplate_100ul_pcr_full_skirt', slot)
          for slot in ['3', '4', '5', '6', '7', '8', '9', '10', '11']]
tiprack = labware.load('opentrons-tiprack-10ul', '1')

# instrument setup
# p300 = instruments.P20_Single(
#     mount='left',
#     tip_racks=[tiprack])

 # initialize pipettes
p20 = instruments.P20_Single_GEN2(
    mount = 'right',
    tip_racks=[tiprack])


def run_custom_protocol(
        transfer_volume: float=100,
        number_of_plates: int=9,
        discard_tip: 'StringSelection...'='False'):

    if discard_tip == 'False':
        discard_tip = False
    else:
        discard_tip = True

    for index, source in enumerate(block.wells()):
        dest = [plate.wells(index) for plate in plates[:number_of_plates]]
        p20.distribute(transfer_volume, source, dest, new_tip='once',
                        trash=discard_tip, touch_tip=True)
        # p20.transfer(transfer_volume, source, dest, new_tip='once', trash=discard_tip, blow_out=False, touch_tip=True)

run_custom_protocol(**{'transfer_volume': 5.0, 'number_of_plates': 4, 'discard_tip': 'True'})
