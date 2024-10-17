// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.19;

interface IZKFirmaDigital {
    function verifyZKFirmaDigitalProof(
        uint nullifierSeed,
        uint nullifier,
        uint signal,
        uint[1] memory revealArray,
        uint[8] memory groth16Proof
    ) external view returns (bool);
}
