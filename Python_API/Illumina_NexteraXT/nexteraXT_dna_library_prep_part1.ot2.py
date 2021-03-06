from opentrons import labware, instruments, robot

"""
Tagment Genomic DNA
Amplify Libraries
"""
# labware setup
gDNA_plate = labware.load('nest_96_wellplate_100ul_pcr_full_skirt', '1')
out_plate = labware.load('nest_96_wellplate_100ul_pcr_full_skirt', '2')
tuberack = labware.load('opentrons_24_tuberack_nest_0.5ml_screwcap', '5')

# reagent setup
atm = tuberack.wells('A1')  # Amplicon Tagment Mix
td = tuberack.wells('B1')  # Tagment DNA Buffer
nt = tuberack.wells('C1')  # Neutralize Tagment Buffer
npm = tuberack.wells('D1')  # Nextera PCR Master Mix
index_7 = tuberack.wells('A2', to='D4')  # Index 1 (i7) adapters
index_5 = tuberack.wells('A5', to='D6')  # Index 2 (i5) adapters

tipracks300 = [labware.load('opentrons_96_tiprack_300ul', slot) for slot in ['3', '4']]
tipracks10 = [labware.load('opentrons_96_tiprack_10ul', slot)
              for slot in ['6', '7', '8', '9']]

# pipette setup
p300 = instruments.p300_single_gen2(
    mount='left',
    tip_racks=tipracks300)

p20 = instruments.P20_Single_gen2(
    mount='right',
    tip_racks=tipracks10)


def run_custom_protocol(
        number_of_samples: int=24):

    # define sample locations
    samples = gDNA_plate.wells()[:number_of_samples]

    if number_of_samples <= 24:
        # index7 = 6
        index5 = 4
        output = [well
                  for col in gDNA_plate.cols('1', to='6')
                  for well in col.wells('A', to='D')]
    else:
        # index7 = 12
        index5 = 8
        output = [well for well in out_plate.wells()][:number_of_samples]

    cols = number_of_samples // index5
    remainder = number_of_samples % index5

    """
    Tagment genomic DNA
    """
    # Add Tagment DNA Buffer to each well
    p300.distribute(10, td, [well.top() for well in samples])

    # Add normalized gDNA to each well
    p20.transfer(5, samples, output, new_tip='always')

    # Add ATM to each well
    for well in output:
        p20.pick_up_tip()
        p20.transfer(5, atm, well, new_tip='never')
        p20.mix(5, 10, well)
        p20.drop_tip()

    robot.pause("Centrifuge at 280 × g at 20°C for 1 minute. Place on the \
        preprogrammed thermal cycler and run the tagmentation program. \
        When the sample reaches 10°C, immediately proceed to the next step \
        because the transposome is still active. Place the plate back to \
        slot 2.")

    # Add Neutralize Tagment Buffer to each well
    p20.transfer(5, nt, output, mix_after=(5, 10), new_tip='always')

    robot.pause("Centrifuge at 280 × g at 20°C for 1 minute. Place the plate \
        back to slot 2.")

    # Incubate at RT for 5 minutes
    p20.delay(minutes=5)

    """
    Amplify Libraries
    """
    # Add each index 1 adapter down each column
    for index, loc in enumerate(range(0, number_of_samples, index5)[:cols]):
        p300.distribute(
            5,
            index_7[index],
            [well.top() for well in output[loc: loc+index5]])

    if remainder:
        index = range(0, number_of_samples, index5)[cols]
        p300.distribute(
            5,
            index_7[cols],
            [well.top() for well in output[index:index+remainder]])

    # Add each index 2 adapter across each row
    for index in range(0, index5):
        if remainder and index < remainder:
            loc = [loc for loc in range(
                index, number_of_samples, index5)][:cols+1]
            dest = [output[i].top() for i in loc]
        else:
            dest = [output[i].top() for i in range(
                index, number_of_samples, index5)][:cols]
        p300.distribute(
            5,
            index_5[index],
            dest)

    # Add Nextera PCR Master Mix to each well
    p300.transfer(15, npm, output, mix_after=(2, 30), new_tip='always')


run_custom_protocol(**{'number_of_samples': 8})
