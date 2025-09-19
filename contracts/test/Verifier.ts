import {
    loadFixture,
    time,
  } from '@nomicfoundation/hardhat-toolbox/network-helpers'
  import { expect } from 'chai'
  import { ethers } from 'hardhat'
  import {
    InitArgs,
    init,
    generateArgs,
    prove,
    artifactUrls,
    ZKFirmaDigitalProof,
    PackedGroth16Proof,
    packGroth16Proof,
    ArtifactsOrigin,
  } from '../../core/src'
  import { testQRData } from '../../circuits/assets/dataInput.json'
  import fs from 'fs'
  import { testPublicKeyHash } from '@anon-aadhaar/core'
  
  describe('VerifyProof', function () {
    this.timeout(0)
  
    async function deployOneYearLockFixture() {
      const Verifier = await ethers.getContractFactory('Verifier')
      const verifier = await Verifier.deploy()
  
      const _verifierAddress = await verifier.getAddress()
  
      const pubkeyHashBigInt = BigInt(testPublicKeyHash).toString()
  
      const ZKFirmaDigitalContract = await ethers.getContractFactory('ZKFirmaDigital')
      const ZKFirmaDigitalVerifier = await ZKFirmaDigitalContract.deploy(
        _verifierAddress,
        pubkeyHashBigInt,
      )
  
      const _ZKFirmaDigitalAddress = await ZKFirmaDigitalVerifier.getAddress()
  
      const ZKFirmaDigitalVote = await ethers.getContractFactory('ZKFirmaDigitalVote')
      const ZKFirmaDigitalVote = await ZKFirmaDigitalVote.deploy(
        'Do you like this app?',
        ['yes', 'no', 'maybe'],
        _ZKFirmaDigitalAddress,
      )
  
      return {
        ZKFirmaDigitalVerifier,
        ZKFirmaDigitalVote,
      }
    }
  
    describe('ZKFirmaDigital Verifier Contract', function () {
      let packedGroth16Proof: PackedGroth16Proof
      let ZKFirmaDigitalProof: ZKFirmaDigitalProof
      let certificate: string
      let user1addres: string
  
      const nullifierSeed = 1234
  
      this.beforeAll(async () => {
        const certificateDirName = __dirname + '/../../circuits/assets'
        certificate = fs
          .readFileSync(certificateDirName + '/testCertificate.pem')
          .toString()
  
        const ZKFirmaDigitalInitArgs: InitArgs = {
          wasmURL: artifactUrls.v2.wasm,
          zkeyURL: artifactUrls.v2.zkey,
          vkeyURL: artifactUrls.v2.vk,
          artifactsOrigin: ArtifactsOrigin.server,
        }
  
        const [user1] = await ethers.getSigners()
        user1addres = user1.address
  
        await init(ZKFirmaDigitalInitArgs)
  
        const args = await generateArgs({
          qrData: testQRData,
          certificateFile: certificate,
          nullifierSeed: nullifierSeed,
          signal: user1addres,
          fieldsToRevealArray: [
            'revealAgeAbove18',
            'revealGender',
            'revealPinCode',
            'revealState',
          ],
        })
  
        const ZKFirmaDigitalCore = await prove(args)
  
        ZKFirmaDigitalProof = ZKFirmaDigitalCore.proof
  
        packedGroth16Proof = packGroth16Proof(ZKFirmaDigitalProof.groth16Proof)
      })
  
      describe('verifyZKFirmaDigitalProof', function () {
        it('Should return true for a valid ZKFirmaDigital proof', async function () {
          const { ZKFirmaDigitalVerifier } = await loadFixture(
            deployOneYearLockFixture,
          )
  
          expect(
            await ZKFirmaDigitalVerifier.verifyZKFirmaDigitalProof(
              nullifierSeed,
              ZKFirmaDigitalProof.nullifier,
              ZKFirmaDigitalProof.timestamp,
              user1addres,
              [
                ZKFirmaDigitalProof.ageAbove18,
                ZKFirmaDigitalProof.gender,
                ZKFirmaDigitalProof.pincode,
                ZKFirmaDigitalProof.state,
              ],
              packedGroth16Proof,
            ),
          ).to.be.equal(true)
        })
  
        it('Should revert for a wrong signal', async function () {
          const { ZKFirmaDigitalVerifier } = await loadFixture(
            deployOneYearLockFixture,
          )
  
          expect(
            await ZKFirmaDigitalVerifier.verifyZKFirmaDigitalProof(
              nullifierSeed,
              ZKFirmaDigitalProof.nullifier,
              ZKFirmaDigitalProof.timestamp,
              40,
              [
                ZKFirmaDigitalProof.ageAbove18,
                ZKFirmaDigitalProof.gender,
                ZKFirmaDigitalProof.pincode,
                ZKFirmaDigitalProof.state,
              ],
              packedGroth16Proof,
            ),
          ).to.be.equal(false)
        })
      })
    })
  
    describe('ZKFirmaDigitalVote contract', function () {
      let packedGroth16Proof: PackedGroth16Proof
      let ZKFirmaDigitalProof: ZKFirmaDigitalProof
      let certificate: string
      let user1addres: string
  
      const nullifierSeed = 0 // proposal index as nullifierSeed
  
      this.beforeAll(async () => {
        const certificateDirName = __dirname + '/../../circuits/assets'
        certificate = fs
          .readFileSync(certificateDirName + '/testCertificate.pem')
          .toString()
  
        const ZKFirmaDigitalInitArgs: InitArgs = {
          wasmURL: artifactUrls.v2.wasm,
          zkeyURL: artifactUrls.v2.zkey,
          vkeyURL: artifactUrls.v2.vk,
          artifactsOrigin: ArtifactsOrigin.server,
        }
  
        const [user1] = await ethers.getSigners()
        user1addres = user1.address
  
        await init(ZKFirmaDigitalInitArgs)
  
        const args = await generateArgs({
          qrData: testQRData,
          certificateFile: certificate,
          nullifierSeed: nullifierSeed,
          signal: user1addres,
        })
  
        const ZKFirmaDigitalCore = await prove(args)
  
        ZKFirmaDigitalProof = ZKFirmaDigitalCore.proof
  
        packedGroth16Proof = packGroth16Proof(ZKFirmaDigitalProof.groth16Proof)
      })
  
      describe('Vote for a proposal', function () {
        it('Should revert if signal is different from senderss address', async function () {
          const { ZKFirmaDigitalVote } = await loadFixture(deployOneYearLockFixture)
  
          const [, , user2] = await ethers.getSigners()
  
          await expect(
            (
              ZKFirmaDigitalVote.connect(user2) as typeof ZKFirmaDigitalVote
            ).voteForProposal(
              0, // proposal index
              0, // proposal index also used as nullifierSeed,
              ZKFirmaDigitalProof.nullifier,
              ZKFirmaDigitalProof.timestamp,
              user1addres,
              [
                ZKFirmaDigitalProof.ageAbove18,
                ZKFirmaDigitalProof.gender,
                ZKFirmaDigitalProof.pincode,
                ZKFirmaDigitalProof.state,
              ],
              packedGroth16Proof,
            ),
          ).to.be.revertedWith('[ZKFirmaDigitalVote]: Wrong user signal sent.')
        })
  
        it('Should verify a proof with right address in signal', async function () {
          const { ZKFirmaDigitalVote } = await loadFixture(deployOneYearLockFixture)
  
          await expect(
            ZKFirmaDigitalVote.voteForProposal(
              0, // proposal index
              0, // proposal index also used as nullifierSeed,
              ZKFirmaDigitalProof.nullifier,
              ZKFirmaDigitalProof.timestamp,
              user1addres,
              [
                ZKFirmaDigitalProof.ageAbove18,
                ZKFirmaDigitalProof.gender,
                ZKFirmaDigitalProof.pincode,
                ZKFirmaDigitalProof.state,
              ],
              packedGroth16Proof,
            ),
          ).to.emit(ZKFirmaDigitalVote, 'Voted')
        })
  
        it('Should revert if timestamp is more than 3hr ago', async function () {
          const { ZKFirmaDigitalVote } = await loadFixture(deployOneYearLockFixture)
  
          // Increase next block time to 5 hours from proof time
          await time.increaseTo(Number(ZKFirmaDigitalProof.timestamp) + 5 * 60 * 60)
  
          await expect(
            ZKFirmaDigitalVote.voteForProposal(
              0, // proposal index
              0, // proposal index also used as nullifierSeed,
              ZKFirmaDigitalProof.nullifier,
              ZKFirmaDigitalProof.timestamp,
              user1addres,
              [
                ZKFirmaDigitalProof.ageAbove18,
                ZKFirmaDigitalProof.gender,
                ZKFirmaDigitalProof.pincode,
                ZKFirmaDigitalProof.state,
              ],
              packedGroth16Proof,
            ),
          ).to.be.revertedWith(
            '[ZKFirmaDigitalVote]: Proof must be generated with Aadhaar data signed less than 3 hours ago.',
          )
        })
      })
    })
  })
  