package com.nishita.jobportal.service;
import com.nishita.jobportal.dto.JobDtos.JobRequest;
import com.nishita.jobportal.entity.*;
import com.nishita.jobportal.repository.*;
import org.junit.jupiter.api.*;
import java.util.Optional;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;
class JobServiceTest{
 private final JobRepository jobs=mock(JobRepository.class);private final CompanyRepository companies=mock(CompanyRepository.class);private final JobService service=new JobService(jobs,companies);
 @Test void rejectsInvertedSalaryRange(){UserAccount recruiter=new UserAccount();recruiter.setId(1L);Company company=new Company();company.setRecruiter(recruiter);when(companies.findById(2L)).thenReturn(Optional.of(company));JobRequest request=new JobRequest(2L,"Engineer","Build services","Remote","Full-time","Java",100000,50000);assertThrows(IllegalArgumentException.class,()->service.create(request,recruiter));verify(jobs,never()).save(any());}
}
