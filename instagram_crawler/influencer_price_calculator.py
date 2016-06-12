class InfluencerPriceCalculator(object):

    CPM_STEP = 0.22
    CPM_BASE = 5
    BASE_ROI = 2.5  
    EXTREME_LOW_ENGAGEMENT_CPM = 3
    ENGAGEMENT_MAX = 10
    ENGAGEMENT_TO_CPM = {engagement: cpm for (engagement, cpm) in
                         [(i, (i - 1) * CPM_STEP + CPM_BASE) for i in range(1, ENGAGEMENT_MAX + 1)]}

    @classmethod
    def calculate_price(cls, followers, avg_likes):
        engagement = (float(avg_likes) / float(followers)) * 100
        engagement_round_int = int(round(engagement))
        # for low engagement, 3$ CPM (divide by base roi will equal 1, but might change in future)
        if engagement_round_int < 1:
            return (cls.EXTREME_LOW_ENGAGEMENT_CPM / cls.BASE_ROI) * (followers / 1000)
        # for extremely high engagement, get max cpm
        if engagement_round_int > cls.ENGAGEMENT_MAX:
            engagement_round_int = cls.ENGAGEMENT_MAX

        cpm = cls.ENGAGEMENT_TO_CPM[engagement_round_int]
        return (cpm / cls.BASE_ROI) * (followers / 1000)