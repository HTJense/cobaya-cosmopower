# Cobaya+CosmoPower

A basic `CosmoPower` theory for `Cobaya`. Calculates the CMB C-ell's from CosmoPower NNs.

See the `example.yaml` file for a basic setup on how to use, simply add your likelihood that takes in Cl's in the `likelihood:` block to use this theory code and update the theory code tags to point it at the pre-trained NNs for Cl calculation. See `CosmoPower` (linked below) for example networks.

# References

[CosmoPower](https://github.com/alessiospuriomancini/cosmopower) was written by [A. Spurio Mancini et al](https://arxiv.org/abs/2106.03846).

[Cobaya](https://github.com/CobayaSampler/cobaya/) was written by [J. Torrado and A. Lewis](https://arxiv.org/abs/2005.05290).
