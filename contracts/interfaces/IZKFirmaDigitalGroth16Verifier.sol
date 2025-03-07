// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.19;

interface IZKFirmaDigitalGroth16Verifier {
    function verifyProof(
        uint[2] calldata _pA,
        uint[2][2] calldata _pB,
        uint[2] calldata _pC,
        uint[5] calldata publicInputs
    ) external view returns (bool);
}
