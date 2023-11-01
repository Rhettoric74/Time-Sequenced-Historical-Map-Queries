from attestation import Attestation
import numpy as np

class NameVariantNode(object):
    def __init__(self, name):
        self.name_variant = name
        self.attestations = []
    def from_json(self, attestations_list):
        for fields_dict in attestations_list:
            if isinstance(fields_dict, dict):
                attestation = Attestation.from_json(fields_dict)
                if attestation.year != None:
                    self.attestations.append(attestation)
    def get_range(self, confidence_threshold = 0):
        """
        Purpose: get the time range of all attestations of this name variant that are above a certain confidence threshold
        Parameters: confidence threshold (number betweeen 0 and 1) representing the minimum confidence score to include an
            attestation in the time range
        Returns: a tuple (min_year, max_year)"""
        min_year = float("inf")
        max_year = - float("inf")
        for attestation in self.attestations:
            if attestation.get_score() > confidence_threshold:
                if attestation.year < min_year:
                    min_year = attestation.year
                if attestation.year > max_year:
                    max_year = attestation.year
            else:
                print(attestation.year, attestation.get_score())
        return (min_year, max_year)
    def get_score(self, confidence_threshold = 0):
        """
        Purpose: calculate a score of how confident the time range for this name variant is.
        Used to determine priority for how to use labels for dating maps.
        Parameters: self, the NameVariantNode object
        Returns: a positive float representing how "confident" the range is.
        """
        # want to reward variants with many attestations
        deg_freedom = len(self.attestations) - 1
        if deg_freedom <= 0:
            return 0
        # want the confidence of each attestation in the range to factor in
        attestations_confidence = np.median([attestation.get_score() for attestation in self.attestations if attestation.get_score() >= confidence_threshold])
        return attestations_confidence * deg_freedom

    def __str__(self):
        return (self.name_variant + "\n" + "Confidence score: " + str(self.get_score()) + 
                "\n" + "\n".join([str(attestation) for attestation in self.attestations]))