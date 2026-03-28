"""
Augusta National course configuration.
Demo representation with 18 holes, par values, and difficulty modifiers.
"""
from src.data.schemas import HoleProfile, CourseProfile


def get_augusta_course() -> CourseProfile:
    """
    Return Augusta National course profile.

    Difficulty scale:
      -0.5 to -0.2 = easier holes
       0.0 = neutral
       0.2 to 0.5 = harder holes
       0.5+ = very difficult holes
    """
    holes = [
        # Front nine
        HoleProfile(hole_number=1, par=4, difficulty=0.1, yardage=445),
        HoleProfile(hole_number=2, par=5, difficulty=-0.1, yardage=575),
        HoleProfile(hole_number=3, par=4, difficulty=0.2, yardage=350),
        HoleProfile(hole_number=4, par=3, difficulty=0.3, yardage=240),
        HoleProfile(hole_number=5, par=4, difficulty=0.4, yardage=495),
        HoleProfile(hole_number=6, par=3, difficulty=0.2, yardage=180),
        HoleProfile(hole_number=7, par=4, difficulty=0.0, yardage=450),
        HoleProfile(hole_number=8, par=5, difficulty=-0.2, yardage=570),
        HoleProfile(hole_number=9, par=4, difficulty=0.1, yardage=460),

        # Back nine
        HoleProfile(hole_number=10, par=4, difficulty=0.2, yardage=495),
        HoleProfile(hole_number=11, par=4, difficulty=0.5, yardage=505),  # Tough hole
        HoleProfile(hole_number=12, par=3, difficulty=0.6, yardage=155),  # Amen Corner
        HoleProfile(hole_number=13, par=5, difficulty=0.1, yardage=510),
        HoleProfile(hole_number=14, par=4, difficulty=0.0, yardage=440),
        HoleProfile(hole_number=15, par=5, difficulty=-0.1, yardage=530),
        HoleProfile(hole_number=16, par=3, difficulty=0.3, yardage=170),
        HoleProfile(hole_number=17, par=4, difficulty=0.2, yardage=440),
        HoleProfile(hole_number=18, par=4, difficulty=0.3, yardage=465),
    ]

    return CourseProfile(
        course_id="augusta_national",
        name="Augusta National Golf Club",
        holes=holes
    )
