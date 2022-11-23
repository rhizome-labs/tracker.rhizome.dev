from fastapi import APIRouter, Query, Request, status
from fastapi.responses import HTMLResponse

from tracker_rhizome_dev import ENV, EXA, TEMPLATES
from tracker_rhizome_dev.app.gov import Gov
from tracker_rhizome_dev.app.icx import Icx
from tracker_rhizome_dev.app.models.icx import Db_ValidatorNodeStatus, Validator
from tracker_rhizome_dev.app.utils import format_number, format_percentage, to_int

router = APIRouter(prefix="/governance")


@router.get(
    "/iiss-overview/", response_class=HTMLResponse, status_code=status.HTTP_200_OK
)
async def get_iiss_overview(request: Request):
    network_info = Icx.get_network_info()

    # Get validator count.
    validator_count = network_info["preps"]
    main_validator_count = (
        network_info["mainPRepCount"] + network_info["extraMainPRepCount"]
    )
    sub_validator_count = validator_count - main_validator_count

    # Get bond requirement.
    bond_requirement = network_info["bondRequirement"] / 100

    # Get reward fund breakdown.
    reward_fund = network_info["rewardFund"]
    i_cps = reward_fund["Icps"]
    i_global = reward_fund["Iglobal"] / EXA
    i_prep = reward_fund["Iprep"]
    i_relay = reward_fund["Irelay"]
    i_voter = reward_fund["Ivoter"]

    # Get ICX delegation details.
    total_bonded_icx = network_info["totalBonded"] / EXA
    total_delegated_icx = network_info["totalDelegated"] / EXA
    total_staked_icx = network_info["totalStake"] / EXA
    total_power = network_info["totalPower"] / EXA

    validators = Gov.get_validators()
    validator_bonds = [
        to_int(validator["bonded"]) / EXA for validator in validators["preps"]
    ]
    nonzero_validator_bonds = [bond for bond in validator_bonds if bond > 0]
    average_bond = sum(nonzero_validator_bonds) / len(nonzero_validator_bonds)

    return TEMPLATES.TemplateResponse(
        "governance/components/iiss_overview.html",
        {
            "request": request,
            "bond_requirement": format_percentage(bond_requirement),
            "total_bonded_icx": format_number(total_bonded_icx, 0),
            "total_delegated_icx": format_number(total_delegated_icx, 0),
            "total_staked_icx": format_number(total_staked_icx, 0),
            "total_power": format_number(total_power, 0),
            "i_global": format_number(i_global, 0),
            "i_cps": i_cps,
            "i_prep": i_prep,
            "i_relay": i_relay,
            "i_voter": i_voter,
            "validator_count": validator_count,
            "main_validator_count": main_validator_count,
            "sub_validator_count": sub_validator_count,
            "average_bond": format_number(average_bond, 0),
        },
    )


@router.get("/validators/", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def get_validators(
    request: Request,
    sort_by: str = Query(
        default="id",
        regex=r"^rank$|^name$|^cps$|^delegation$|^power$|^bond$|^productivity$|^rewards$",
    ),
    sort_dir: str = "asc",
):
    validators = Gov.get_validators()
    network_info = Icx.get_network_info()
    icx_usd_price = Icx.get_icx_usd_price()
    formatted_validators = [
        Validator(
            irep_update_block_height=validator["irepUpdateBlockHeight"],
            last_height=validator["lastHeight"],
            node_address=validator["nodeAddress"],
            p2p_endpoint=validator["p2pEndpoint"],
            total_blocks=validator["totalBlocks"],
            validated_blocks=validator["validatedBlocks"],
            **validator,
            icx_usd_price=icx_usd_price,
            network_info=network_info,
        )
        for validator in validators["preps"]
    ]

    if sort_by == "bond":
        formatted_validators = sorted(
            formatted_validators, key=lambda x: x.bonded_ratio["default"]
        )
    #    elif sort_by == "cps":
    #        formatted_validators = sorted(
    #            formatted_validators, key=lambda x: x.cps_sponsored_projects
    #        )
    elif sort_by == "delegation":
        formatted_validators = sorted(
            formatted_validators, key=lambda x: x.delegated["default"]
        )
    elif sort_by == "name":
        formatted_validators = sorted(formatted_validators, key=lambda x: x.name)
    elif sort_by == "productivity":
        formatted_validators = sorted(
            formatted_validators, key=lambda x: x.productivity["default"]
        )

    if sort_dir == "desc":
        formatted_validators.reverse()

    return TEMPLATES.TemplateResponse(
        "governance/components/validators.html",
        {
            "request": request,
            "validators": formatted_validators,
            "sort_by": sort_by,
            "sort_dir": sort_dir,
        },
    )
