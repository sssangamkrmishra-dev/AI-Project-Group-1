"""
Student Placement Readiness Bayesian Network
============================================================================

Updated Network Structure (7 Nodes):
    [Mock Performance]  [Consistency]  [Rejections]  [Resume Quality]
            ↓                  ↓             ↓                ↓
            └──→ [Skill Level] ←─────────────┘                │
                       ↓                     ↓                │
                       └──→ [Confidence State] ←──────────────┘
                                     ↓                         │
                       [Placement Readiness] ←─────────────────┘

Evidence Nodes: MockPerformance, Consistency, Rejections, ResumeQuality
Hidden Nodes: SkillLevel, ConfidenceState
Target Node: PlacementReadiness
"""

import numpy as np
import json
import os
from typing import Dict, List, Tuple
from collections import defaultdict


class BayesianNetwork:
    """
    Bayesian Network for Student Placement Readiness Assessment
    with Resume Quality (ATS Score) as 4th evidence variable
    """
    
    def __init__(self, cpt_file='cpt_data.json'):
        """
        Initialize the Bayesian Network with CPTs from JSON file
        
        Args:
            cpt_file: Path to JSON file containing CPT data
        """
        self.cpt_file = cpt_file
        self.load_cpds()
        self.structure = self._define_structure()
        
    def load_cpds(self):
        """Load Conditional Probability Tables from JSON file"""
        try:
            with open(self.cpt_file, 'r') as f:
                data = json.load(f)
            
            self.metadata = data['metadata']
            self.node_definitions = data['node_definitions']
            self.cpds = {
                'MockPerformance': data['prior_probabilities']['MockPerformance'],
                'Consistency': data['prior_probabilities']['Consistency'],
                'Rejections': data['prior_probabilities']['Rejections'],
                'ResumeQuality': data['prior_probabilities']['ResumeQuality'],
                'SkillLevel': data['conditional_probabilities']['SkillLevel']['cpt'],
                'ConfidenceState': data['conditional_probabilities']['ConfidenceState']['cpt'],
                'PlacementReadiness': data['conditional_probabilities']['PlacementReadiness']['cpt']
            }
            
            print(f"✓ Successfully loaded CPTs from {self.cpt_file}")
            print(f"  Network version: {self.metadata['version']}")
            print(f"  Total nodes: {self.metadata['total_nodes']}")
            print(f"  Evidence nodes: {self.metadata['evidence_nodes']}")
            
        except FileNotFoundError:
            print(f"✗ Error: CPT file '{self.cpt_file}' not found!")
            print("  Creating default CPTs in memory...")
            self._create_default_cpds()
            
    def _create_default_cpds(self):
        """Create default CPTs if JSON file is not found"""
        self.metadata = {
            "version": "2.0",
            "total_nodes": 7,
            "evidence_nodes": 4
        }
        
        self.cpds = {
            'MockPerformance': {
                'Excellent': 0.15, 'Good': 0.30, 'Average': 0.40, 'Poor': 0.15
            },
            'Consistency': {
                'HighlyConsistent': 0.20, 'Moderate': 0.35, 'Irregular': 0.30, 'Rare': 0.15
            },
            'Rejections': {
                'None': 0.25, '1-2': 0.35, '3-5': 0.25, 'MoreThan5': 0.15
            },
            'ResumeQuality': {
                'High': 0.25, 'Medium': 0.50, 'Low': 0.25
            },
            'SkillLevel': {
                'Excellent_HighlyConsistent': {'High': 0.85, 'Medium': 0.13, 'Low': 0.02},
                'Average_Moderate': {'High': 0.30, 'Medium': 0.50, 'Low': 0.20},
                # ... (abbreviated for default case)
            },
            'ConfidenceState': {
                'None_High': {'Confident': 0.70, 'Neutral': 0.25, 'Anxious': 0.04, 'Frustrated': 0.01},
                # ... (abbreviated)
            },
            'PlacementReadiness': {
                'High_Confident_High': {'WellPrepared': 0.90, 'ModeratelyPrepared': 0.08, 'Underprepared': 0.01, 'HighRisk': 0.01},
                # ... (abbreviated)
            }
        }
        
    def _define_structure(self) -> Dict:
        """Define the network structure (DAG)"""
        return {
            'nodes': [
                'MockPerformance',
                'Consistency', 
                'Rejections',
                'ResumeQuality',
                'SkillLevel',
                'ConfidenceState',
                'PlacementReadiness'
            ],
            'edges': [
                ('MockPerformance', 'SkillLevel'),
                ('Consistency', 'SkillLevel'),
                ('Rejections', 'ConfidenceState'),
                ('SkillLevel', 'ConfidenceState'),
                ('SkillLevel', 'PlacementReadiness'),
                ('ConfidenceState', 'PlacementReadiness'),
                ('ResumeQuality', 'PlacementReadiness')
            ]
        }
    
    def inference(self, evidence: Dict[str, str]) -> Dict:
        """
        Perform Variable Elimination inference
        
        Args:
            evidence: Dictionary with observed values
                     e.g., {'MockPerformance': 'Average', 'Consistency': 'Moderate', 
                            'Rejections': '1-2', 'ResumeQuality': 'Medium'}
        
        Returns:
            Dictionary containing posterior probabilities for all variables
        """
        # Validate evidence
        required_keys = ['MockPerformance', 'Consistency', 'Rejections', 'ResumeQuality']
        for key in required_keys:
            if key not in evidence:
                raise ValueError(f"Missing required evidence: {key}")
        
        # Step 1: Calculate P(SkillLevel | MockPerformance, Consistency)
        skill_key = f"{evidence['MockPerformance']}_{evidence['Consistency']}"
        
        if skill_key not in self.cpds['SkillLevel']:
            raise KeyError(f"Invalid evidence combination: {skill_key}")
            
        skill_probs = self.cpds['SkillLevel'][skill_key].copy()
        
        # Step 2: Calculate P(ConfidenceState | Rejections, SkillLevel)
        # Marginalize over SkillLevel
        confidence_probs = defaultdict(float)
        
        for skill_level in ['High', 'Medium', 'Low']:
            conf_key = f"{evidence['Rejections']}_{skill_level}"
            
            if conf_key not in self.cpds['ConfidenceState']:
                raise KeyError(f"Invalid evidence combination: {conf_key}")
                
            conf_dist = self.cpds['ConfidenceState'][conf_key]
            
            for conf_state, prob in conf_dist.items():
                confidence_probs[conf_state] += prob * skill_probs[skill_level]
        
        # Step 3: Calculate P(PlacementReadiness | SkillLevel, ConfidenceState, ResumeQuality)
        # Marginalize over both SkillLevel and ConfidenceState
        readiness_probs = defaultdict(float)
        
        for skill_level in ['High', 'Medium', 'Low']:
            for conf_state in ['Confident', 'Neutral', 'Anxious', 'Frustrated']:
                read_key = f"{skill_level}_{conf_state}_{evidence['ResumeQuality']}"
                
                if read_key not in self.cpds['PlacementReadiness']:
                    raise KeyError(f"Invalid evidence combination: {read_key}")
                    
                read_dist = self.cpds['PlacementReadiness'][read_key]
                joint_prob = skill_probs[skill_level] * confidence_probs[conf_state]
                
                for read_state, prob in read_dist.items():
                    readiness_probs[read_state] += prob * joint_prob
        
        # Normalize readiness probabilities
        total = sum(readiness_probs.values())
        if total > 0:
            readiness_probs = {k: v/total for k, v in readiness_probs.items()}
        
        return {
            'SkillLevel': dict(skill_probs),
            'ConfidenceState': dict(confidence_probs),
            'PlacementReadiness': dict(readiness_probs)
        }
    
    def get_most_likely_state(self, distribution: Dict[str, float]) -> Tuple[str, float]:
        """Get the most likely state from a probability distribution"""
        return max(distribution.items(), key=lambda x: x[1])
    
    def identify_risk_factors(self, evidence: Dict, inference_result: Dict) -> List[str]:
        """
        Identify risk factors based on evidence and inference results
        
        Args:
            evidence: Input evidence
            inference_result: Results from inference
        
        Returns:
            List of identified risk factors
        """
        risk_factors = []
        
        # Check rejections
        if evidence['Rejections'] in ['3-5', 'MoreThan5']:
            risk_factors.append('High rejection count affecting psychological state')
        
        # Check consistency
        if evidence['Consistency'] in ['Irregular', 'Rare']:
            risk_factors.append('Inconsistent preparation pattern detected')
        
        # Check mock performance
        if evidence['MockPerformance'] in ['Poor', 'Average']:
            risk_factors.append('Technical skills need significant improvement')
        
        # Check resume quality (NEW)
        if evidence['ResumeQuality'] == 'Low':
            risk_factors.append('Resume quality below ATS threshold (ATS score < 40)')
        
        # Check confidence state probabilities
        conf_probs = inference_result['ConfidenceState']
        if conf_probs.get('Anxious', 0) > 0.3 or conf_probs.get('Frustrated', 0) > 0.2:
            risk_factors.append('High probability of stress/frustration detected')
        
        # Check skill level
        skill_probs = inference_result['SkillLevel']
        if skill_probs.get('Low', 0) > 0.5:
            risk_factors.append('Low skill level requires intensive training')
        
        # Check readiness vs confidence mismatch
        read_probs = inference_result['PlacementReadiness']
        if (read_probs.get('Underprepared', 0) + read_probs.get('HighRisk', 0)) > 0.6:
            risk_factors.append('CRITICAL: Requires immediate intervention and support')
        
        return risk_factors
    
    def generate_report(self, evidence: Dict, inference_result: Dict) -> str:
        """
        Generate a comprehensive assessment report
        
        Args:
            evidence: Input evidence
            inference_result: Results from inference
        
        Returns:
            Formatted report string
        """
        report = []
        report.append("="*70)
        report.append("STUDENT PLACEMENT READINESS ASSESSMENT REPORT")
        report.append("="*70)
        report.append("")
        
        # Evidence
        report.append("INPUT EVIDENCE:")
        report.append("-" * 70)
        for key, value in evidence.items():
            if key == 'ResumeQuality':
                ats_ranges = {'High': '71-100', 'Medium': '41-70', 'Low': '<40'}
                report.append(f"  {key:25s}: {value} (ATS Score: {ats_ranges.get(value, 'N/A')})")
            else:
                report.append(f"  {key:25s}: {value}")
        report.append("")
        
        # Skill Level
        report.append("INFERRED SKILL LEVEL:")
        report.append("-" * 70)
        skill_dist = inference_result['SkillLevel']
        most_likely_skill, skill_prob = self.get_most_likely_state(skill_dist)
        report.append(f"  Most Likely State: {most_likely_skill} ({skill_prob*100:.2f}%)")
        report.append("  Probability Distribution:")
        for state, prob in sorted(skill_dist.items(), key=lambda x: -x[1]):
            report.append(f"    {state:15s}: {prob*100:6.2f}% {'█' * int(prob*50)}")
        report.append("")
        
        # Confidence State
        report.append("INFERRED CONFIDENCE STATE:")
        report.append("-" * 70)
        conf_dist = inference_result['ConfidenceState']
        most_likely_conf, conf_prob = self.get_most_likely_state(conf_dist)
        report.append(f"  Most Likely State: {most_likely_conf} ({conf_prob*100:.2f}%)")
        report.append("  Probability Distribution:")
        for state, prob in sorted(conf_dist.items(), key=lambda x: -x[1]):
            report.append(f"    {state:15s}: {prob*100:6.2f}% {'█' * int(prob*50)}")
        report.append("")
        
        # Placement Readiness
        report.append("PLACEMENT READINESS ASSESSMENT:")
        report.append("=" * 70)
        read_dist = inference_result['PlacementReadiness']
        most_likely_read, read_prob = self.get_most_likely_state(read_dist)
        report.append(f"  PRIMARY ASSESSMENT: {most_likely_read} ({read_prob*100:.2f}%)")
        report.append("")
        report.append("  Detailed Probability Distribution:")
        for state, prob in sorted(read_dist.items(), key=lambda x: -x[1]):
            report.append(f"    {state:20s}: {prob*100:6.2f}% {'█' * int(prob*50)}")
        report.append("")
        
        # Risk Factors
        risk_factors = self.identify_risk_factors(evidence, inference_result)
        if risk_factors:
            report.append("IDENTIFIED RISK FACTORS:")
            report.append("-" * 70)
            for i, factor in enumerate(risk_factors, 1):
                report.append(f"  {i}. {factor}")
            report.append("")
        
        # Recommendations
        report.append("RECOMMENDED ACTIONS:")
        report.append("-" * 70)
        if most_likely_read == 'WellPrepared':
            report.append("  • Continue current preparation strategy")
            report.append("  • Focus on mock interviews with top companies")
            report.append("  • Work on advanced problem-solving")
            if evidence['ResumeQuality'] != 'High':
                report.append("  • Consider further resume optimization for premium positions")
        elif most_likely_read == 'ModeratelyPrepared':
            report.append("  • Increase preparation intensity")
            report.append("  • Focus on weak areas identified in mocks")
            report.append("  • Practice more company-specific questions")
            if evidence['ResumeQuality'] == 'Low':
                report.append("  • URGENT: Resume needs immediate improvement (ATS score < 40)")
        elif most_likely_read == 'Underprepared':
            report.append("  • URGENT: Develop structured preparation plan")
            report.append("  • Daily practice schedule needed")
            report.append("  • Consider placement coaching/mentorship")
            report.append("  • Focus on fundamental concepts")
            if evidence['ResumeQuality'] == 'Low':
                report.append("  • Resume rewrite required (current ATS score insufficient)")
        else:  # HighRisk
            report.append("  • CRITICAL: Immediate intervention required")
            report.append("  • Meet with placement officer/counselor")
            report.append("  • Consider stress management support")
            report.append("  • Intensive skill development program needed")
            if evidence['ResumeQuality'] == 'Low':
                report.append("  • Professional resume writing service recommended")
            report.append("  • Explore alternative career paths if needed")
        
        report.append("")
        report.append("="*70)
        
        return "\n".join(report)


def main():
    """Main function with test cases"""
    
    # Initialize Bayesian Network (loads CPTs from JSON)
    print("\n" + "="*70)
    print("BAYESIAN NETWORK FOR STUDENT PLACEMENT READINESS")
    print("="*70)
    print()
    
    bn = BayesianNetwork('cpt_data.json')
    
    print("\nNetwork Structure:")
    print("-" * 70)
    print("Nodes:", bn.structure['nodes'])
    print("\nEdges (Causal Relationships):")
    for parent, child in bn.structure['edges']:
        print(f"  {parent} → {child}")
    print("\n" + "=" * 70)
    print("\n")
    
    # Test Case 1: Well-Prepared Student with Excellent Resume
    print("\nTEST CASE 1: Well-Prepared Student with Strong Resume")
    print("=" * 70)
    evidence1 = {
        'MockPerformance': 'Excellent',
        'Consistency': 'HighlyConsistent',
        'Rejections': 'None',
        'ResumeQuality': 'High'
    }
    result1 = bn.inference(evidence1)
    print(bn.generate_report(evidence1, result1))
    
    # Test Case 2: Average Student with Pressure and Weak Resume
    print("\n\nTEST CASE 2: Average Student with Mounting Pressure and Weak Resume")
    print("=" * 70)
    evidence2 = {
        'MockPerformance': 'Average',
        'Consistency': 'Irregular',
        'Rejections': '3-5',
        'ResumeQuality': 'Low'
    }
    result2 = bn.inference(evidence2)
    print(bn.generate_report(evidence2, result2))
    
    # Test Case 3: High-Risk Student
    print("\n\nTEST CASE 3: High-Risk Student (Critical Intervention Needed)")
    print("=" * 70)
    evidence3 = {
        'MockPerformance': 'Poor',
        'Consistency': 'Rare',
        'Rejections': 'MoreThan5',
        'ResumeQuality': 'Low'
    }
    result3 = bn.inference(evidence3)
    print(bn.generate_report(evidence3, result3))
    
    # Test Case 4: Good Skills but Poor Resume (NEW - shows Resume impact)
    print("\n\nTEST CASE 4: Good Skills Held Back by Poor Resume")
    print("=" * 70)
    evidence4 = {
        'MockPerformance': 'Good',
        'Consistency': 'Moderate',
        'Rejections': '1-2',
        'ResumeQuality': 'Low'
    }
    result4 = bn.inference(evidence4)
    print(bn.generate_report(evidence4, result4))
    
    # Export results to JSON
    results_json = {
        'test_case_1': {
            'description': 'Well-Prepared with Strong Resume',
            'evidence': evidence1,
            'inference': result1
        },
        'test_case_2': {
            'description': 'Average Student with Pressure and Weak Resume',
            'evidence': evidence2,
            'inference': result2
        },
        'test_case_3': {
            'description': 'High-Risk Critical Case',
            'evidence': evidence3,
            'inference': result3
        },
        'test_case_4': {
            'description': 'Good Skills but Poor Resume',
            'evidence': evidence4,
            'inference': result4
        }
    }
    
    with open('bayesian_network_results.json', 'w') as f:
        json.dump(results_json, f, indent=2)
    
    print("\n\n" + "="*70)
    print("Results exported to 'bayesian_network_results.json'")
    print("="*70)
    print()


if __name__ == "__main__":
    main()