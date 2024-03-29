import os
import cosmopower as cp
import numpy as np

from cobaya.theories.cosmo import BoltzmannBase
from cobaya.typing import InfoDict

"""
  Simple CosmoPower theory wrapper for Cobaya.
  
  author: Hidde T. Jense
"""
class CosmoPower(BoltzmannBase):
    network_path : str = "cptheory/training_data"
    cmb_tt_nn_filename : str = "cmb_TT_NN"
    cmb_te_pcaplusnn_filename : str = "cmb_TE_PCAplusNN"
    cmb_ee_nn_filename : str = "cmb_EE_NN"
    
    extra_args: InfoDict = { }
    
    aliases: dict = {
        "omega_b" : [ "ombh2" ],
        "omega_cdm" : [ "omch2" ],
        "ln10^{10}A_s" : [ "logA" ],
        "n_s" : [ "ns" ],
        "h" : [ ],
        "tau_reio" : [ "tau" ],
    }
    
    def initialize(self):
        super().initialize()
        
        self.cp_tt_nn = cp.cosmopower_NN(restore = True, restore_filename = os.path.join(self.network_path, self.cmb_tt_nn_filename))
        self.cp_te_nn = cp.cosmopower_PCAplusNN(restore = True, restore_filename = os.path.join(self.network_path, self.cmb_te_pcaplusnn_filename))
        self.cp_ee_nn = cp.cosmopower_NN(restore = True, restore_filename = os.path.join(self.network_path, self.cmb_ee_nn_filename))
        
        self.lmax_theory = self.extra_args.get("lmax_theory", 2508)
        
        self.log.info(f"Loaded CosmoPower from directory {self.network_path}")
    
    def calculate(self, state, want_derived = True, **params):
        cmb_params = { }
        
        for par in self.aliases:
            if par in params:
                cmb_params[par] = [params[par]]
            else:
                for alias in self.aliases[par]:
                    if alias in params:
                        cmb_params[par] = [params[alias]]
                        break
        
        state["tt"] = self.cp_tt_nn.ten_to_predictions_np(cmb_params)[0,:]
        state["te"] = self.cp_te_nn.predictions_np(cmb_params)[0,:]
        state["ee"] = self.cp_ee_nn.ten_to_predictions_np(cmb_params)[0,:]
    
    def get_Cl(self, ell_factor = True, units = "FIRASmuK2"):
        cls_old = self.current_state.copy()
        
        cls = { k : np.zeros((self.lmax_theory,)) for k in [ "tt", "te", "ee" ] }
        cls["ell"] = np.arange(self.lmax_theory)
        
        ls = 2 + np.arange(cls_old["tt"].shape[0])
        
        cmb_fac = self._cmb_unit_factor(units, 2.726)
        
        if ell_factor:
            ls_fac = ls * (ls + 1.0) / (2.0 * np.pi)
        else:
            ls_fac = 1.0
        
        for k in [ "tt", "te", "ee" ]:
            cls[k][ls] = cls_old[k] * ls_fac * cmb_fac ** 2.0
        
        return cls
    
    def get_can_support_params(self):
        return [ "omega_b", "omega_cdm", "h", "logA", "ns", "tau_reio" ]
    
    def _cmb_unit_factor(self, units, T_cmb):
        units_factors = {
            "1": 1,
            "muK2": T_cmb * 1.0e6,
            "K2": T_cmb,
            "FIRASmuK2": 2.7255e6,
            "FIRASK2": 2.7255
        }
        
        try:
            return units_factors[units]
        except KeyError:
            raise LoggedError(self.log, "Units '%s' not recognized. Use one of %s.", units, list(units_factors))
