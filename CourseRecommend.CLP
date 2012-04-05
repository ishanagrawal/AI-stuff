;;template to store all data related to a module
(deftemplate module-data
	(slot name)
	(multislot prereq)
	(slot offered)
	(slot difficulty)
	(slot time)
)

;;template to store the modules already taken by the student
(deftemplate modules_taken
	(multislot module)
)

;;modules already taken by the student to satisfy prereqs
(deffacts taken
(modules_taken 
	(module cs3215 cs2271 cs1102))
)

;;database of modules
(deffacts modules
	(module-data (name cs4273) (prereq cs2271 cs3215)
		(offered yes) (difficulty Diff) (time Mon))
	(module-data (name cs3202) (prereq cs1102)
		(offered yes) (difficulty Diff) (time Fri))
	(module-data (name cs3243) (prereq cs1102 cs1231)
		(offered yes) (difficulty Easy) (time Tue))
	(module-data (name cs4202) (prereq cs1102)
		(offered yes) (difficulty Diff) (time Thur))
	(module-data (name cs5506) (prereq cs3215)
		(offered no) (difficulty Diff) (time Mon))
	(module-data (name cs3453) (prereq cs1102)
		(offered yes) (difficulty Easy) (time Wed))
	(module-data (name cs3220) (prereq cs1231)
		(offered yes) (difficulty Easy) (time Mon))
	(module-data (name cs4271) (prereq cs1102)
		(offered yes) (difficulty Diff) (time Fri))
	(module-data (name cs3553) (prereq cs1231)
		(offered no) (difficulty Easy) (time Wed))
)		

;;rule to filter out modules not offered this semster	
(defrule module_offered
	(declare (salience 100))
	?module-fact <- (module-data (name ?name) (offered no))
	=>
	;;(printout t "At offered" crlf)
	(retract ?module-fact) 
	(assert (mod_is_offered yes))
)

;;rule to filter out module for which student does not satisfy prereqs
(defrule module_prereq
(declare (salience 90))
(mod_is_offered yes)
?test <- (modules_taken (module $?modules))
?module-fact <- (module-data (prereq $?prereq&:(not (subsetp $?prereq (create$ ?modules) ))))
=>	
(retract ?module-fact)
;;(printout t "At prereqs" crlf)
(assert (prereq_satisfied yes))
)

;;rule to filter out modules which clash with each other
(defrule module_clash
(declare (salience 80))
(prereq_satisfied yes)
?a <- (module-data (name ?name1)(time ?t1)) 
?b <- (module-data (name ?name2)(time ?t2))
(and (test (neq ?name1 ?name2))  (test (eq ?t1 ?t2))) 
=>
;;(printout t ?name1 . ?name2 . ?t1 crlf)
;;(printout t "List of module that student can take for this semester:" crlf)
;;(printout t "module clash" crlf)
(retract ?a)
(assert (print_out yes))
)

;;rule to print out the allowed modules
(defrule print_results
(module-data (name ?name) (offered ?offer)(difficulty ?diff) (time ?time))
(print_out yes)
=>
(printout t "Module: "  ?name " offered: " ?offer  " Time: "  ?time  "  Difficulty level: "  ?diff crlf)
)

