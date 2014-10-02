SELECT COUNT(DISTINCT gs.id) AS gs_count
     , COUNT(gbg.game_id) AS gbg_count
     , COUNT(pbg.game_id) AS pbg_count

FROM nhl.game_summaries AS gs

LEFT JOIN nhl.game_by_game AS gbg
       ON gbg.game_id = gs.id

LEFT JOIN nhl.penalties_by_game AS pbg
       ON pbg.game_id = gs.id

WHERE gs.season = 2014

GROUP BY gs.id
HAVING gs_count != 1
    OR gbg_count != 4
    OR pbg_count != 4
;

SELECT COUNT(*)
FROM nhl.game_by_game AS g
WHERE g.season = 2014
;

SELECT COUNT(*)
FROM nhl.penalties_by_game AS g
WHERE g.season = 2014
;




SELECT g.*

     # cumlative signals
     , COUNT(DISTINCT g2.game_id) AS game_of_season
     , COUNT(DISTINCT IF(g2.location = 'AWAY', g2.game_id, NULL)) AS away_games
     , COUNT(DISTINCT IF(g2.location = 'HOME', g2.game_id, NULL)) AS home_games

     # shots
     , SUM(g2.shots_for) AS cumulative_shots_for
     , SUM(IF(g2.location = 'AWAY', g2.shots_for, 0)) AS cumulative_away_shots_for
     , SUM(IF(g2.location = 'HOME', g2.shots_for, 0)) AS cumulative_home_shots_for
     , SUM(IF(g2.result = 'R' AND g2.decision = 'W', g2.shots_for, 0)) AS cumulative_wins_shots_for
     , SUM(IF(g2.result = 'R' AND g2.decision = 'L', g2.shots_for, 0)) AS cumulative_losses_shots_for

     , SUM(g2.shots_against) AS cumulative_shots_against
     , SUM(IF(g2.location = 'AWAY', g2.shots_against, 0)) AS cumulative_away_shots_against
     , SUM(IF(g2.location = 'HOME', g2.shots_against, 0)) AS cumulative_home_shots_against
     , SUM(IF(g2.result = 'R' AND g2.decision = 'W', g2.shots_against, 0)) AS cumulative_wins_shots_against
     , SUM(IF(g2.result = 'R' AND g2.decision = 'L', g2.shots_against, 0)) AS cumulative_losses_shots_against

     # goals
     , SUM(g2.goals_for) AS cumulative_goals_for
     , SUM(IF(g2.location = 'AWAY', g2.goals_for, 0)) AS cumulative_away_goals_for
     , SUM(IF(g2.location = 'HOME', g2.goals_for, 0)) AS cumulative_home_goals_for
     , SUM(IF(g2.result = 'R' AND g2.decision = 'W', g2.goals_for, 0)) AS cumulative_wins_goals_for
     , SUM(IF(g2.result = 'R' AND g2.decision = 'L', g2.goals_for, 0)) AS cumulative_losses_goals_for
     , SUM(g2.goals_against) AS cumulative_goals_against
     , SUM(IF(g2.location = 'AWAY', g2.goals_against, 0)) AS cumulative_away_goals_against
     , SUM(IF(g2.location = 'HOME', g2.goals_against, 0)) AS cumulative_away_goals_against
     , SUM(IF(g2.result = 'R' AND g2.decision = 'W', g2.goals_against, 0)) AS cumulative_wins_goals_against
     , SUM(IF(g2.result = 'R' AND g2.decision = 'L', g2.goals_against, 0)) AS cumulative_losses_goals_against

     , SUM(g2.powerplay_goals) AS cumulative_powerplay_goals
     , SUM(IF(g2.location = 'AWAY', g2.powerplay_goals, 0)) AS cumulative_away_powerplay_goals
     , SUM(IF(g2.location = 'HOME', g2.powerplay_goals, 0)) AS cumulative_home_powerplay_goals
     , SUM(g2.powerplay_goals_against) AS cumulative_powerplay_goals_against
     , SUM(IF(g2.location = 'AWAY', g2.powerplay_goals_against, 0)) AS cumulative_away_powerplay_goals_against
     , SUM(IF(g2.location = 'HOME', g2.powerplay_goals_against, 0)) AS cumulative_home_powerplay_goals_against

     , LENGTH(GROUP_CONCAT(g2.scorers)) - LENGTH(REPLACE(GROUP_CONCAT(g2.scorers), "s", "")) AS shorthanded_goals_for

     # opportunities
     , SUM(g2.powerplay_opportunities) AS cumulative_powerplay_opportunities
     , SUM(IF(g2.location = 'AWAY', g2.powerplay_opportunities, 0)) AS cumulative_away_powerplay_opportunities
     , SUM(IF(g2.location = 'HOME', g2.powerplay_opportunities, 0)) AS cumulative_home_powerplay_opportunities
     , SUM(g2.times_shorthanded) AS cumulative_times_shorthanded
     , SUM(IF(g2.location = 'AWAY', g2.times_shorthanded, 0)) AS cumulative_away_times_shorthanded
     , SUM(IF(g2.location = 'HOME', g2.times_shorthanded, 0)) AS cumulative_home_times_shorthanded

     # outcome signals
     , COUNT(DISTINCT IF(g2.result = 'R', g2.game_id, NULL)) AS regulation_games
     , COUNT(DISTINCT IF(g2.result = 'R' AND g2.decision = 'W', g2.game_id, NULL)) AS regulation_wins
     , COUNT(DISTINCT IF(g2.result = 'R' AND g2.decision = 'L', g2.game_id, NULL)) AS regulation_losses
     , COUNT(DISTINCT IF(g2.result = 'OT', g2.game_id, NULL)) AS overtime_games
     , COUNT(DISTINCT IF(g2.result = 'OT' AND g2.decision = 'W', g2.game_id, NULL)) AS overtime_wins
     , COUNT(DISTINCT IF(g2.result = 'OT' AND g2.decision = 'O', g2.game_id, NULL)) AS overtime_losses
     , COUNT(DISTINCT IF(g2.result = 'SO', g2.game_id, NULL)) AS shootout_games
     , COUNT(DISTINCT IF(g2.result = 'SO' AND g2.decision = 'W', g2.game_id, NULL)) AS shootout_wins
     , COUNT(DISTINCT IF(g2.result = 'SO' AND g2.decision = 'O', g2.game_id, NULL)) AS shootout_losses

     # outcome by location signals
     , COUNT(DISTINCT IF(g2.result = 'R' AND g2.location = 'AWAY', g2.game_id, NULL)) AS regulation_away_games
     , COUNT(DISTINCT IF(g2.result = 'R' AND g2.location = 'HOME', g2.game_id, NULL)) AS regulation_home_games
     , COUNT(DISTINCT IF(g2.result = 'R' AND g2.decision = 'W' AND g2.location = 'AWAY', g2.game_id, NULL)) AS regulation_away_wins
     , COUNT(DISTINCT IF(g2.result = 'R' AND g2.decision = 'W' AND g2.location = 'HOME', g2.game_id, NULL)) AS regulation_home_wins
     , COUNT(DISTINCT IF(g2.result = 'R' AND g2.decision = 'L' AND g2.location = 'AWAY', g2.game_id, NULL)) AS regulation_away_losses
     , COUNT(DISTINCT IF(g2.result = 'R' AND g2.decision = 'L' AND g2.location = 'HOME', g2.game_id, NULL)) AS regulation_home_losses
     , COUNT(DISTINCT IF(g2.result = 'OT' AND g2.location = 'AWAY', g2.game_id, NULL)) AS overtime_away_games
     , COUNT(DISTINCT IF(g2.result = 'OT' AND g2.location = 'HOME', g2.game_id, NULL)) AS overtime_home_games
     , COUNT(DISTINCT IF(g2.result = 'OT' AND g2.decision = 'W' AND g2.location = 'AWAY', g2.game_id, NULL)) AS overtime_away_wins
     , COUNT(DISTINCT IF(g2.result = 'OT' AND g2.decision = 'W' AND g2.location = 'HOME', g2.game_id, NULL)) AS overtime_home_wins
     , COUNT(DISTINCT IF(g2.result = 'OT' AND g2.decision = 'O' AND g2.location = 'AWAY', g2.game_id, NULL)) AS overtime_away_losses
     , COUNT(DISTINCT IF(g2.result = 'OT' AND g2.decision = 'O' AND g2.location = 'HOME', g2.game_id, NULL)) AS overtime_home_losses
     , COUNT(DISTINCT IF(g2.result = 'SO' AND g2.location = 'AWAY', g2.game_id, NULL)) AS shootout_away_games
     , COUNT(DISTINCT IF(g2.result = 'SO' AND g2.location = 'HOME', g2.game_id, NULL)) AS shootout_home_games
     , COUNT(DISTINCT IF(g2.result = 'SO' AND g2.decision = 'W' AND g2.location = 'AWAY', g2.game_id, NULL)) AS shootout_away_wins
     , COUNT(DISTINCT IF(g2.result = 'SO' AND g2.decision = 'W' AND g2.location = 'HOME', g2.game_id, NULL)) AS shootout_home_wins
     , COUNT(DISTINCT IF(g2.result = 'SO' AND g2.decision = 'O' AND g2.location = 'AWAY', g2.game_id, NULL)) AS shootout_away_losses
     , COUNT(DISTINCT IF(g2.result = 'SO' AND g2.decision = 'O' AND g2.location = 'HOME', g2.game_id, NULL)) AS shootout_home_losses

FROM nhl.game_by_game AS g

JOIN nhl.game_by_game AS g2
  ON g2.team = g.team
 AND g2.season = g.season
 AND g2.game_date <= g.game_date

WHERE g.season = 2014

GROUP BY CONCAT(g.game_id, g.team)
ORDER BY g.game_date DESC
;



