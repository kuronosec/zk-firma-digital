pragma circom 2.1.9;

include "circomlib/circuits/bitify.circom";
include "circomlib/circuits/poseidon.circom";
include "./helpers/signature.circom";
include "./helpers/nullifier.circom";


/// @title FirmaDigitalCRVerifier
/// @notice This circuit verifies the user certificate of Firma Digital CR using RSA signature
/// @param n RSA pubic key size per chunk
/// @param k Number of chunks the RSA public key is split into
/// @param maxDataLength Maximum length of the data
/// @input certDataPadded cert data without the signature; assumes elements to be bytes; remaining space is padded with 0
/// @input certDataPaddedLength Length of padded cert data
/// @input signature RSA signature
/// @input pubKey RSA public key (of the government)
/// @input revealAgeAbove18 Flag to reveal age is above 18
/// @input nullifierSeed A random value used as an input to compute the nullifier; for example: applicationId, actionId
/// @input public signalHash Any message to commit to (to make it part of the proof)
/// @output pubkeyHash Poseidon hash of the RSA public key (after merging nearby chunks)
/// @output nullifier A unique value derived from nullifierSeed and Aadhaar data to nullify the proof/user
/// @output timestamp Timestamp of when the data was signed - extracted and converted to Unix timestamp
/// @output ageAbove18 Boolean flag indicating age is above 18; 0 if not revealed
/// @output gender Gender 70(F) or 77(M); 0 if not revealed
/// @output pinCode Pin code of the address as int; 0 if not revealed
/// @output state State packed as int (reverse order); 0 if not revealed
template FirmaDigitalCRVerifier(n, k, maxDataLength) {
    signal input certDataPadded[maxDataLength];
    signal input certDataPaddedLength;
    signal input signature[k];
    signal input pubKey[k];
    signal input revealAgeAbove18;

    // Public inputs
    signal input nullifierSeed;
    signal input signalHash;

    signal output pubkeyHash;
    signal output nullifier;
    signal output ageAbove18;

    // Assert `certDataPaddedLength` fits in `ceil(log2(maxDataLength))`
    component n2bHeaderLength = Num2Bits(log2Ceil(maxDataLength));
    n2bHeaderLength.in <== certDataPaddedLength;

    // Verify the RSA signature
    component signatureVerifier = SignatureVerifier(n, k, maxDataLength);
    signatureVerifier.certDataPadded <== certDataPadded;
    signatureVerifier.certDataPaddedLength <== certDataPaddedLength;
    signatureVerifier.pubKey <== pubKey;
    signatureVerifier.signature <== signature;
    pubkeyHash <== signatureVerifier.pubkeyHash;

    // Assert data between certDataPaddedLength and maxDataLength is zero
    AssertZeroPadding(maxDataLength)(certDataPadded, certDataPaddedLength);
    
    // Reveal extracted data
    revealAgeAbove18 * (revealAgeAbove18 - 1) === 0;

    // TODO: do something smarter here
    // For Firma CR, age is always above 18
    ageAbove18 <== revealAgeAbove18 * 1;

    // TODO: create an actual Nullifier
    // Calculate nullifier
    nullifier <== Nullifier(n, k)(nullifierSeed, signature);
    
    // Dummy square to prevent signal tampering
    // (in rare cases where non-constrained inputs are ignored)
    signal signalHashSquare <== signalHash * signalHash;
}
