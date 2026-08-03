package com.nishita.jobportal.repository;
import com.nishita.jobportal.entity.Company;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
public interface CompanyRepository extends JpaRepository<Company,Long>{ List<Company> findByRecruiterId(Long recruiterId); }
