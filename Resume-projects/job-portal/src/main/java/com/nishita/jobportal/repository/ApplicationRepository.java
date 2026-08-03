package com.nishita.jobportal.repository;
import com.nishita.jobportal.entity.*;
import org.springframework.data.domain.*;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import java.util.*;
public interface ApplicationRepository extends JpaRepository<JobApplication,Long>{
 boolean existsByJobIdAndCandidateId(Long jobId,Long candidateId);
 Page<JobApplication> findByCandidateId(Long candidateId,Pageable pageable);
 @Query("select a from JobApplication a where a.job.company.recruiter.id=:recruiterId and (:q='' or lower(a.candidate.name) like lower(concat('%',:q,'%')) or lower(a.candidate.email) like lower(concat('%',:q,'%')) or lower(a.job.title) like lower(concat('%',:q,'%'))) and (:status is null or a.status=:status)")
 Page<JobApplication> searchRecruiter(@Param("recruiterId") Long recruiterId,@Param("q") String q,@Param("status") ApplicationStatus status,Pageable pageable);
 long countByJobCompanyRecruiterId(Long recruiterId);
 long countByJobCompanyRecruiterIdAndStatus(Long recruiterId,ApplicationStatus status);
}
