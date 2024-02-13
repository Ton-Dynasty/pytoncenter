from datetime import datetime, timedelta

import pytest

from pytoncenter.v3.models import (
    GetBlockRequest,
    GetJettonBurnsRequest,
    GetJettonTransfersRequest,
    GetNFTTransfersRequest,
)


class TestDecoder:

    def test_start_end_utime_failed(self):
        start_utime = datetime.now()
        end_utime = start_utime - timedelta(days=100)
        with pytest.raises(ValueError):
            GetJettonBurnsRequest(start_utime=start_utime, end_utime=end_utime)
            GetJettonTransfersRequest(start_utime=start_utime, end_utime=end_utime)
            GetNFTTransfersRequest(start_utime=start_utime, end_utime=end_utime)
            GetBlockRequest(start_utime=start_utime, end_utime=end_utime)

    def test_start_end_lt_failed(self):
        start_lt = 100
        end_lt = 99
        with pytest.raises(ValueError):
            GetJettonBurnsRequest(start_lt=start_lt, end_lt=end_lt)
            GetJettonTransfersRequest(start_lt=start_lt, end_lt=end_lt)
            GetNFTTransfersRequest(start_lt=start_lt, end_lt=end_lt)
            GetBlockRequest(start_lt=start_lt, end_lt=end_lt)
