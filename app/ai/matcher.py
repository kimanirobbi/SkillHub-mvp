"""
AI-based professional-job matching system using sentence transformers.
Handles both skill matching and geographical proximity.
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging
import numpy as np
from math import radians, sin, cos, sqrt, atan2
from sentence_transformers import SentenceTransformer, util
from functools import lru_cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
DEFAULT_MAX_DISTANCE_KM = 50
SIMILARITY_WEIGHT = 0.7
DISTANCE_WEIGHT = 0.3
MODEL_NAME = "all-MiniLM-L6-v2"

@lru_cache(maxsize=1)
def get_model():
    """Cache the model to avoid reloading it on every request."""
    return SentenceTransformer(MODEL_NAME)

def cosine_similarity(a, b) -> float:
    """Calculate cosine similarity between two vectors."""
    return float(util.cos_sim(a, b).item())

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees).
    Returns distance in kilometers.
    """
    if None in (lat1, lon1, lat2, lon2):
        return None
        
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    R = 6371  # Radius of Earth in kilometers
    return R * c

@dataclass
class Professional:
    """Data class for professional information."""
    id: int
    skills: List[str]
    profession: str
    experience_years: int = 0
    rating: float = 0.0
    latitude: Optional[float] = None
    longitude: Optional[float] = None

@dataclass
class Job:
    """Data class for job information."""
    id: int
    title: str
    description: str
    profession: str
    location_lat: float
    location_lng: float

class ProfessionalMatcher:
    """
    Matches professionals to jobs using semantic similarity and geolocation.
    """
    
    def __init__(
        self,
        similarity_weight: float = 0.5,
        distance_weight: float = 0.2,
        experience_weight: float = 0.1,
        rating_weight: float = 0.1,
        rate_weight: float = 0.1,
        max_distance_km: float = DEFAULT_MAX_DISTANCE_KM
    ):
        """
        Initialize the matcher with custom weights and thresholds.
        
        Args:
            similarity_weight: Weight for skill similarity (0-1)
            distance_weight: Weight for distance (0-1)
            experience_weight: Weight for years of experience (0-1)
            rating_weight: Weight for rating (0-1)
            rate_weight: Weight for hourly rate (0-1)
            max_distance_km: Maximum distance to consider (in km)
        """
        weights = [similarity_weight, distance_weight, experience_weight, rating_weight, rate_weight]
        if not all(0 <= w <= 1 for w in weights) or abs(sum(weights) - 1.0) > 1e-6:
            raise ValueError("Weights must be between 0 and 1 and sum to 1")
            
        self.similarity_weight = similarity_weight
        self.distance_weight = distance_weight
        self.experience_weight = experience_weight
        self.rating_weight = rating_weight
        self.rate_weight = rate_weight
        self.max_distance_km = max_distance_km
        self.model = get_model()
        
        logger.info(
            f"Initialized ProfessionalMatcher with weights: "
            f"similarity={similarity_weight}, distance={distance_weight}, "
            f"experience={experience_weight}, rating={rating_weight}, rate={rate_weight}, "
            f"max_distance={max_distance_km}km"
        )
    
    def _get_job_embedding(self, job: Job) -> np.ndarray:
        """Generate embedding for job."""
        job_text = f"{job.title} {job.description} {job.profession}"
        return self.model.encode(job_text, convert_to_tensor=True)
    
    def _get_professional_embedding(self, professional: Professional) -> np.ndarray:
        """Generate embedding for professional."""
        skills_text = " ".join(professional.skills) if professional.skills else professional.profession
        return self.model.encode(skills_text, convert_to_tensor=True)
    
    def _calculate_normalized_distance_score(
        self, 
        lat1: float, 
        lon1: float, 
        lat2: float, 
        lon2: float
    ) -> float:
        """
        Calculate normalized distance score (0-1) where 1 is closest.
        Returns 0 if distance exceeds max_distance_km.
        """
        try:
            distance = calculate_distance(lat1, lon1, lat2, lon2)
            if distance > self.max_distance_km:
                return 0.0
            return 1 - (distance / self.max_distance_km)
        except ValueError as e:
            logger.warning(f"Error calculating distance: {e}")
            return 0.0
    
    def match(
        self,
        job: Job,
        professionals: List[Professional],
        top_n: int = 5,
        min_score: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        Match professionals to a job.
        
        Args:
            job: The job to match against
            professionals: List of professionals to consider
            top_n: Maximum number of matches to return
            min_score: Minimum score threshold for matches (0-1)
            
        Returns:
            List of dicts containing match information, sorted by score
        """
        if not professionals:
            logger.warning("No professionals provided for matching")
            return []
            
        logger.info(f"Matching job '{job.title}' against {len(professionals)} professionals")
        
        # Pre-compute job embedding once
        try:
            job_embedding = self._get_job_embedding(job)
        except Exception as e:
            logger.error(f"Error generating job embedding: {e}")
            return []
        
        matches = []
        
        for pro in professionals:
            try:
                # Calculate skill similarity
                pro_embedding = self._get_professional_embedding(pro)
                similarity = cosine_similarity(job_embedding, pro_embedding)
                
                # Calculate distance score if location data is available
                if None not in (job.location_lat, job.location_lng, pro.latitude, pro.longitude):
                    distance_score = self._calculate_normalized_distance_score(
                        job.location_lat, job.location_lng,
                        pro.latitude, pro.longitude
                    )
                else:
                    distance_score = 0.5  # Neutral score if location data is missing
                
                # Calculate combined score
                combined_score = (
                    (similarity * self.similarity_weight) +
                    (distance_score * self.distance_weight)
                )
                
                # Apply minimum score threshold
                if combined_score >= min_score:
                    distance = calculate_distance(
                        job.location_lat, job.location_lng,
                        pro.latitude, pro.longitude
                    )
                    matches.append({
                        "professional": pro,
                        "score": round(combined_score, 3),
                        "similarity": round(similarity, 3),
                        "distance_score": round(distance_score, 3),
                        "distance_km": round(distance, 2) if distance is not None else None
                    })
                    
            except Exception as e:
                logger.error(f"Error processing professional {getattr(pro, 'id', 'unknown')}: {e}")
                continue
        
        # Sort by score (descending) and take top N
        matches.sort(key=lambda x: x["score"], reverse=True)
        
        logger.info(f"Found {len(matches)} matches (min_score={min_score})")
        return matches[:top_n]

def match_professionals(
    job: Job,
    professionals: List[Professional],
    max_distance_km: float = DEFAULT_MAX_DISTANCE_KM,
    top_n: int = 5
) -> List[Dict[str, Any]]:
    """
    Convenience function for simple matching.
    
    Args:
        job: The job to match against
        professionals: List of professionals to consider
        max_distance_km: Maximum distance in kilometers
        top_n: Maximum number of results to return
        
    Returns:
        List of matched professionals with scores
    """
    matcher = ProfessionalMatcher(max_distance_km=max_distance_km)
    return matcher.match(job, professionals, top_n=top_n)
