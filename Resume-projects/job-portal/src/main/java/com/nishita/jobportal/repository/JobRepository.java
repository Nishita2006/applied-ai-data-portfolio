package com.nishita.jobportal.repository;
import com.nishita.jobportal.entity.*;
import org.springframework.data.domain.*;
import org.springframework.data.jpa.repository.*;
import org.springframework.data.repository.query.Param;
public interface JobRepository extends JpaRepository<JobPosting,Long>{
 @Query("select j from JobPosting j where j.status=:status and (:q='' or lower(j.title) like lower(concat('%',:q,'%')) or lower(j.company.name) like lower(concat('%',:q,'%')) or lower(j.skills) like lower(concat('%',:q,'%'))) and (:location='' or lower(j.location) like lower(concat('%',:location,'%')))")
 Page<JobPosting> search(@Param("q") String q,@Param("location") String location,@Param("status") JobStatus status,Pageable pageable);
 Page<JobPosting> findByCompanyRecruiterId(Long recruiterId,Pageable pageable);
}
