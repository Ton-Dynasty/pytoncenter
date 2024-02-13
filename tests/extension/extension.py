from tonpy import CellSlice

from pytoncenter.address import Address
from pytoncenter.extension.message import JettonMessage
from pytoncenter.utils import encode_base64


class TestJettonParse:
    def test_jetton_internal_transfer_parse(self):

        # https://testnet.tonviewer.com/transaction/b9638bbcc640b0cdd559c1be8344c73da14e3c91f7f59f250b9a8a38e063d8ba
        raw_body = encode_base64(
            "b5ee9c720101020100a10001ad178d4519000000000000000034c4b3f80052ea860872970f38347c8a4eb7149232cef52c45ac96eaf1e4fbfeca6fef25cb000a5d50c10e52e1e7068f9149d6e2924659dea588b592dd5e3c9f7fd94dfde4b952e7ddb00201008a010000000000000000000000000000000000000000000000000000000000000016000000010000000000000000000000000000000000000000000000000147ae147ae147ae"
        )
        cs = CellSlice(raw_body)
        msg = JettonMessage.InternalTransfer.parse(cs)
        assert msg.query_id == 0
        assert msg.amount == 4999999
        assert msg.sender == Address("0:29754304394b879c1a3e45275b8a4919677a9622d64b7578f27dff6537f792e5")
        assert msg.response_address == Address("0:29754304394b879c1a3e45275b8a4919677a9622d64b7578f27dff6537f792e5")
        assert msg.forward_ton_amount == 3120000000
        assert msg.forward_payload is not None
        oralce_opcode = msg.forward_payload.load_uint(8)
        expire_at = msg.forward_payload.load_uint(256)
        assert oralce_opcode == 1  # Tick Message
        assert expire_at != 0

    def test_jetton_excess(self):
        # https://testnet.tonviewer.com/transaction/ee014cc0d95cd5589951956b11095de7dcb6288a126397a55f789a962f3d815f
        raw_body = encode_base64("b5ee9c7201010101000e000018d53276db0000000000000000")
        cs = CellSlice(raw_body)
        msg = JettonMessage.Excess.parse(cs)
        assert msg.query_id == 0

    def test_jetton_transfer(self):
        # https://testnet.tonviewer.com/transaction/64b0320c972ca8b0815798705dca60b8c28afdc8e5d8aa08e790d851b4dda22f
        raw_body = encode_base64(
            "b5ee9c720101020100a10001ad0f8a7ea5000000000000000034c4b3f8017bc28408f06d3fc030d138584d9fcb47783984a2c899f8ac8a2fda3678a085fd000a5d50c10e52e1e7068f9149d6e2924659dea588b592dd5e3c9f7fd94dfde4b94973eed80101008a010000000000000000000000000000000000000000000000000000000000000016000000010000000000000000000000000000000000000000000000000147ae147ae147ae"
        )
        cs = CellSlice(raw_body)
        msg = JettonMessage.Transfer.parse(cs)
        assert msg.query_id == 0
        assert msg.amount == 4999999
        assert msg.destination == Address("kQC94UIEeDaf4BhonCwmz-WjvBzCUWRM_FZFF-0bPFBC_pDZ")
        assert msg.response_destination == Address("0QApdUMEOUuHnBo-RSdbikkZZ3qWItZLdXjyff9lN_eS5Zib")
        assert msg.custom_payload == None
        assert msg.forward_ton_amount == 3120000000
        assert msg.forward_payload is not None
